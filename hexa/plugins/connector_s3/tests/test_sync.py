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
            role_arn="test-arn-arn-arn-arn",
            default_region="eu-central-1",
        )
        cls.bucket = Bucket.objects.create(name="test-bucket")

    @mock_s3
    @mock_sts
    def test_empty_sync(self):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket="test-bucket")
        self.assertEqual(self.bucket.object_set.count(), 0)

        self.bucket.sync()

        self.assertQuerysetEqual(self.bucket.object_set.all(), [])

    @mock_s3
    @mock_sts
    def test_base_sync(self):
        s3_client = boto3.client("s3")
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
        s3_client = boto3.client("s3")
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
        s3_client = boto3.client("s3")
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
            ("added.csv", False),
            ("a_dir/", False),
            ("a_dir/keep_me.csv", False),
            ("delete_me.csv", True),
            ("other_dir/", False),  # new file
            ("other_dir/leave_me.csv", False),  # new file
        ]
        self.assertQuerysetEqual(
            self.bucket.object_set.all(), expected, lambda x: (x.key, x.orphan)
        )

    @mock_s3
    @mock_sts
    def test_re_uploaded_orphan(self):
        s3_client = boto3.client("s3")
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
