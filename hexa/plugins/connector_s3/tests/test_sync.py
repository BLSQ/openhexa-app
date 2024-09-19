import boto3
from django.test import override_settings
from moto import mock_aws

from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.test import TestCase
from hexa.plugins.connector_s3.models import Bucket

from .mocks.s3_credentials_mock import get_s3_mocked_env


@override_settings(**get_s3_mocked_env())
class SyncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bucket = Bucket.objects.create(name="test-bucket")

    @mock_aws
    def test_empty_sync(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        self.assertEqual(self.bucket.object_set.count(), 0)

        self.bucket.sync()

        self.assertQuerySetEqual(self.bucket.object_set.all(), [])

    @mock_aws
    def test_base_sync(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="base.csv", Body="test")
        s3_client.put_object(
            Bucket="test-bucket", Key="a_dir/without_extension", Body="test"
        )
        s3_client.put_object(
            Bucket="test-bucket", Key="a_dir/a_subdir/stuff.csv", Body="test"
        )

        self.bucket.sync()

        expected = [
            ("a_dir/", "directory"),
            ("a_dir/a_subdir/", "directory"),
            ("a_dir/a_subdir/stuff.csv", "file"),
            ("a_dir/without_extension", "file"),
            ("base.csv", "file"),
        ]
        self.assertQuerySetEqual(
            self.bucket.object_set.all(), expected, lambda x: (x.key, x.type)
        )

        # Sync again, should not differ
        result = self.bucket.sync()
        result.identical = 5
        self.assertQuerySetEqual(
            self.bucket.object_set.all(), expected, lambda x: (x.key, x.type)
        )

    @mock_aws
    def test_metadata(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="metadata.csv", Body="test")
        s3_client.put_object(
            Bucket="test-bucket", Key="another_dir/without_extension", Body="test"
        )
        s3_client.put_object(
            Bucket="test-bucket",
            Key="another_dir/another_subdir/a_file.csv",
            Body="test",
        )

        # Test
        self.bucket.sync()

        expected = [
            ("another_dir/", "directory", "/", 0),
            ("another_dir/another_subdir/", "directory", "another_dir/", 0),
            (
                "another_dir/another_subdir/a_file.csv",
                "file",
                "another_dir/another_subdir/",
                4,
            ),
            ("another_dir/without_extension", "file", "another_dir/", 4),
            ("metadata.csv", "file", "/", 4),
        ]
        self.assertQuerySetEqual(
            self.bucket.object_set.all(),
            expected,
            lambda x: (x.key, x.type, x.parent_key, x.size),
        )

    @mock_aws
    def test_sync_remove_add_edit(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        delete_me = s3_client.put_object(
            Bucket="test-bucket", Key="delete_me.csv", Body="delete_me_content"
        )
        keep_me = s3_client.put_object(
            Bucket="test-bucket", Key="a_dir/keep_me.csv", Body="keep_me_content"
        )
        leave_me = s3_client.put_object(
            Bucket="test-bucket", Key="other_dir/leave_me.csv", Body="leave_me_content"
        )

        # Sync a first time
        result = self.bucket.sync()
        self.assertEqual(
            DatasourceSyncResult(datasource=self.bucket, created=5), result
        )

        self.assertEqual(self.bucket.object_set.all().count(), 5)
        self.assertEqual(
            delete_me["ETag"],
            f'"{self.bucket.object_set.get(key="delete_me.csv").etag}"',
        )
        self.assertEqual(
            keep_me["ETag"],
            f'"{self.bucket.object_set.get(key="a_dir/keep_me.csv").etag}"',
        )
        self.assertEqual(
            leave_me["ETag"],
            f'"{self.bucket.object_set.get(key="other_dir/leave_me.csv").etag}"',
        )

        # Remove a file
        s3_client.delete_object(Bucket="test-bucket", Key="delete_me.csv")
        # Add a new file
        s3_client.put_object(
            Bucket="test-bucket", Key="added.csv", Body="added_content"
        )
        # Update another one
        keep_me_updated = s3_client.put_object(
            Bucket="test-bucket", Key="a_dir/keep_me.csv", Body="keep_me_content_new"
        )

        # Sync again
        result = self.bucket.sync()
        self.assertEqual(
            DatasourceSyncResult(
                datasource=self.bucket, created=1, updated=1, identical=3, deleted=1
            ),
            result,
        )

        # The ETag should be updated
        self.assertEqual(
            keep_me_updated["ETag"],
            f'"{self.bucket.object_set.get(key="a_dir/keep_me.csv").etag}"',
        )

        expected = [
            "a_dir/",
            "a_dir/keep_me.csv",
            "added.csv",
            "other_dir/",  # new file
            "other_dir/leave_me.csv",  # new file
        ]
        result = [x.key for x in self.bucket.object_set.all()]
        result = sorted(result)
        self.assertEqual(result, expected)

    @mock_aws
    def test_double_etag(self):
        """
        Upload 2x the same file with different names
        Sync
        Delete one on s3
        Resync
        One should have disappeared from OH
        """
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        s3_client.put_object(Bucket="test-bucket", Key="original.csv", Body="content")
        s3_client.put_object(Bucket="test-bucket", Key="dupe.csv", Body="content")
        s3_client.put_object(Bucket="test-bucket", Key="third.csv", Body="content")

        self.bucket.sync()
        self.assertEqual(self.bucket.object_set.exclude(type="directory").count(), 3)

        s3_client.delete_object(Bucket="test-bucket", Key="dupe.csv")
        s3_client.delete_object(Bucket="test-bucket", Key="third.csv")

        self.bucket.sync()
        self.assertEqual(self.bucket.object_set.exclude(type="directory").count(), 1)

    @mock_aws
    def test_slash_directory(self):
        """Objects with a key that start with / are valid - but S3 will consider this first slash as a directory
        named "/". It's not a big deal but our sync system has trouble processing them, due to an issue with s3fs
        that strip slashes at the beginning of keys, resulting in an endless recursion issue.
        """
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        # Create object with a key that starts with "/"
        s3_client.put_object(
            Bucket="test-bucket", Key="/imabouttomessthingsup.csv", Body="boom"
        )
        self.bucket.sync()

        self.assertEqual(self.bucket.object_set.count(), 1)

    @mock_aws
    def test_dir_structure(self):
        """A list of files with different path should be indexed as a set of dir and files"""
        self.assertEqual(self.bucket.object_set.count(), 0)

        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        # Create object with a key that starts with "/"
        s3_client.put_object(Bucket="test-bucket", Key="dir1/", Body="")
        s3_client.put_object(Bucket="test-bucket", Key="dir1/file1", Body="K")
        s3_client.put_object(Bucket="test-bucket", Key="dir1/file2", Body="L")
        s3_client.put_object(Bucket="test-bucket", Key="dir2/fileA", Body="M")
        s3_client.put_object(Bucket="test-bucket", Key="dir2/fileB", Body="N")
        s3_client.put_object(
            Bucket="test-bucket", Key="dir3/dir4/dir5/dir6/fileC", Body="N"
        )

        self.bucket.sync()
        self.assertEqual(self.bucket.object_set.count(), 11)
        self.assertEqual(self.bucket.object_set.filter(type="directory").count(), 6)
        self.assertEqual(self.bucket.object_set.filter(type="file").count(), 5)
