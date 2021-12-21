import boto3
from django import test
from moto import mock_s3, mock_sts

from hexa.catalog.sync import DatasourceSyncResult
from hexa.plugins.connector_s3.models import Bucket, Credentials


class SyncTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credentials = Credentials.objects.create(
            username="test-username",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        cls.bucket = Bucket.objects.create(name="test-bucket")

    @mock_s3
    @mock_sts
    def test_empty_sync(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        self.assertEqual(self.bucket.object_set.count(), 0)

        self.bucket.sync()

        self.assertQuerysetEqual(self.bucket.object_set.all(), [])

    @mock_s3
    @mock_sts
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
        self.assertQuerysetEqual(
            self.bucket.object_set.all(), expected, lambda x: (x.key, x.type)
        )

        # Sync again, should not differ
        result = self.bucket.sync()
        result.identical = 5
        self.assertQuerysetEqual(
            self.bucket.object_set.all(), expected, lambda x: (x.key, x.type)
        )

    @mock_s3
    @mock_sts
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
        self.assertQuerysetEqual(
            self.bucket.object_set.all(),
            expected,
            lambda x: (x.key, x.type, x.parent_key, x.size),
        )

    @mock_s3
    @mock_sts
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
                datasource=self.bucket, created=1, updated=1, identical=3, orphaned=1
            ),
            result,
        )

        # The ETag should be updated
        self.assertEqual(
            keep_me_updated["ETag"],
            f'"{self.bucket.object_set.get(key="a_dir/keep_me.csv").etag}"',
        )

        expected = [
            ("a_dir/", False),
            ("a_dir/keep_me.csv", False),
            ("added.csv", False),
            ("delete_me.csv", True),
            ("other_dir/", False),  # new file
            ("other_dir/leave_me.csv", False),  # new file
        ]
        result = [(x.key, x.orphan) for x in self.bucket.object_set.all()]
        result = sorted(result)
        self.assertEqual(result, expected)

    @mock_s3
    @mock_sts
    def test_re_uploaded_orphan(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        # Create orphan
        s3_client.put_object(Bucket="test-bucket", Key="dir/orphan.csv", Body="orphan")
        self.bucket.sync()
        s3_client.delete_object(Bucket="test-bucket", Key="dir/orphan.csv")
        self.bucket.sync()

        orphan_file = self.bucket.object_set.get(key="dir/orphan.csv")
        orphan_dir = self.bucket.object_set.get(key="dir/")
        self.assertTrue(orphan_file.orphan)
        self.assertTrue(orphan_dir.orphan)

        # Re-upload orphan
        s3_client.put_object(Bucket="test-bucket", Key="dir/orphan.csv", Body="orphan")
        self.bucket.sync()

        orphan_file = self.bucket.object_set.get(key="dir/orphan.csv")
        orphan_dir = self.bucket.object_set.get(key="dir/")
        self.assertFalse(orphan_file.orphan)
        self.assertFalse(orphan_dir.orphan)

    @mock_s3
    @mock_sts
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
        self.assertEqual(self.bucket.object_set.exclude(type="directory").count(), 3)

        dupe = self.bucket.object_set.get(key="dupe.csv")
        self.assertTrue(dupe.orphan)

        third = self.bucket.object_set.get(key="third.csv")
        self.assertTrue(third.orphan)

        original = self.bucket.object_set.get(key="original.csv")
        self.assertFalse(original.orphan)

    @mock_s3
    @mock_sts
    def test_new_file_matches_old_one(self):
        """
        Add a file
        sync
        remove it
        sync
        add it elsewhere
        sync
        -> metadata should be transferred, we should have no orphans
        """
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        s3_client.put_object(Bucket="test-bucket", Key="original.csv", Body="content")

        self.bucket.sync()
        self.assertEqual(self.bucket.object_set.count(), 1)
        original = self.bucket.object_set.get(key="original.csv")
        self.assertFalse(original.orphan)

        s3_client.delete_object(Bucket="test-bucket", Key="original.csv")
        self.bucket.sync()
        after_delete = self.bucket.object_set.get(key="original.csv")
        self.assertTrue(after_delete.orphan)
        self.assertEqual(after_delete.pk, original.pk)

        s3_client.put_object(
            Bucket="test-bucket", Key="new-location.csv", Body="content"
        )
        self.bucket.sync()

        self.assertEqual(self.bucket.object_set.count(), 1)
        re_added = self.bucket.object_set.get(key="new-location.csv")
        self.assertEqual(re_added.pk, original.pk)
        self.assertEqual(self.bucket.object_set.filter(orphan=True).count(), 0)

    @mock_s3
    @mock_sts
    def test_slash_directory(self):
        """Objects with a key that start with / are valid - but S3 will consider this first slash as a directory
        named "/". It's not a big deal but our sync system has trouble processing them, due to an issue with s3fs
        that strip slashes at the beginning of keys, resulting in an endless recursion issue."""

        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        # Create object with a key that starts with "/"
        s3_client.put_object(
            Bucket="test-bucket", Key="/imabouttomessthingsup.csv", Body="boom"
        )
        self.bucket.sync()

        self.assertEqual(self.bucket.object_set.count(), 1)

    @mock_s3
    @mock_sts
    def test_dir_structure(self):
        """a list of files with different path should be indexed as a set of dir and files"""

        self.assertEqual(self.bucket.object_set.count(), 0)

        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")

        # Create object with a key that starts with "/"
        s3_client.put_object(Bucket="test-bucket", Key="dir1/", Body="")
        s3_client.put_object(Bucket="test-bucket", Key="dir1/file1", Body="K")
        s3_client.put_object(Bucket="test-bucket", Key="dir1/file2", Body="L")
        s3_client.put_object(Bucket="test-bucket", Key="dir2/fileA", Body="M")
        s3_client.put_object(Bucket="test-bucket", Key="dir2/fileB", Body="N")

        self.bucket.sync()
        self.assertEqual(self.bucket.object_set.count(), 6)
        self.assertEqual(self.bucket.object_set.filter(type="directory").count(), 2)
        self.assertEqual(self.bucket.object_set.filter(type="file").count(), 4)
