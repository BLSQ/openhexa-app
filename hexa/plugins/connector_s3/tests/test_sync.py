from unittest.mock import MagicMock, patch

import boto3
from moto import mock_s3

from django import test

from hexa.catalog.sync import DatasourceSyncResult
from hexa.plugins.connector_s3.models import (
    Credentials,
    Bucket,
)


class SyncTest(test.TestCase):

    bucket_name = "test-bucket"

    def setUp(self):
        #
        self.s3_mock = mock_s3()
        self.s3_mock.start()

        self.generate_sts_buckets_credentials = MagicMock()
        self.generate_sts_buckets_credentials.return_value = {
            "AccessKeyId": "testing",
            "SecretAccessKey": "testing",
            "SessionToken": "testing",
        }

        self.patcher = patch(
            "hexa.plugins.connector_s3.models.generate_sts_buckets_credentials",
            self.generate_sts_buckets_credentials,
        )
        self.patcher.start()

        self.client = boto3.client("s3")
        self.s3_bucket = self.client.create_bucket(Bucket=self.bucket_name)

        self.CREDENTIALS = Credentials.objects.create(
            username="test-username", role_arn="test-arn-arn-arn-arn"
        )
        self.bucket = Bucket.objects.create(name=self.bucket_name)

    def tearDown(self):
        self.patcher.stop()
        self.s3_mock.stop()

    def put_object(self, /, key, bucket=bucket_name, content=None):
        if content is None:
            content = f"{key} - fake content"
        return self.client.put_object(Bucket=bucket, Body=content, Key=key)

    def delete_object(self, /, key, bucket=bucket_name):
        return self.client.delete_object(Bucket=bucket, Key=key)

    def test_empty_sync(self):
        self.assertEqual(self.bucket.object_set.count(), 0)

        self.bucket.sync()

        self.assertEqual(self.generate_sts_buckets_credentials.call_count, 1)
        self.assertQuerysetEqual(self.bucket.object_set.all(), [])

    def test_base_sync(self):
        # Setup
        self.put_object(key="base.csv")
        self.put_object(key="dir1/without_extension")
        self.put_object(key="dir1/dir2/subdir.csv")

        # Test
        self.bucket.sync()

        expected = [
            ("base.csv", "file"),
            ("dir1/", "directory"),
            ("dir1/dir2/", "directory"),
            ("dir1/dir2/subdir.csv", "file"),
            ("dir1/without_extension", "file"),
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

    def test_metadata(self):
        # Setup
        self.put_object(key="base.csv")
        self.put_object(key="dir1/without_extension")
        self.put_object(key="dir1/dir2/subdir.csv")

        # Test
        self.bucket.sync()

        expected = [
            ("base.csv", "file", "/", 23),
            ("dir1/", "directory", "/", 0),
            ("dir1/dir2/", "directory", "dir1/", 0),
            ("dir1/dir2/subdir.csv", "file", "dir1/dir2/", 35),
            ("dir1/without_extension", "file", "dir1/", 37),
        ]
        self.assertQuerysetEqual(
            self.bucket.object_set.all(),
            expected,
            lambda x: (x.key, x.type, x.parent_key, x.size),
        )

    def test_sync_remove_add_edit(self):
        # Setup
        base_original = self.put_object(key="base.csv")
        self.put_object(key="dir1/without_extension")
        self.put_object(key="dir1/dir2/subdir.csv")

        # Sync a first time
        result = self.bucket.sync()
        assert result.created == 5

        self.assertEqual(self.bucket.object_set.all().count(), 5)
        self.assertEqual(
            base_original["ETag"],
            f'"{self.bucket.object_set.get(key="base.csv").etag}"',
        )

        # Remove a file
        self.delete_object(key="dir1/dir2/subdir.csv")
        # Add a new file
        new = self.put_object(key="dir1/dir2/new.csv")
        # Update another one
        base2 = self.put_object(key="base.csv", content="another-content")

        # Sync again
        result = self.bucket.sync()
        self.assertEqual(
            {
                "created": 1,
                "updated": 1,
                "identical": 3,
                "orphaned": 1,
            },
            {
                "created": result.created,
                "updated": result.updated,
                "identical": result.identical,
                "orphaned": result.orphaned,
            },
        )

        # The ETag should be updated
        self.assertEqual(
            base2["ETag"], f'"{self.bucket.object_set.get(key="base.csv").etag}"'
        )

        expected = [
            ("base.csv", False),
            ("dir1/", False),
            ("dir1/dir2/", False),
            ("dir1/dir2/new.csv", False),  # new file
            ("dir1/dir2/subdir.csv", True),  # was deleted -> orphan
            ("dir1/without_extension", False),
        ]
        self.assertQuerysetEqual(
            self.bucket.object_set.all(), expected, lambda x: (x.key, x.orphan)
        )
