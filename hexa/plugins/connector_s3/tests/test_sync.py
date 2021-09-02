from unittest.mock import MagicMock, patch

import boto3
from moto import mock_s3

from django import test
from hexa.plugins.connector_s3.models import (
    Credentials,
    Bucket,
)


class SyncTest(test.TestCase):
    mock_s3 = mock_s3()
    bucket_name = "test-bucket"

    def setUp(self):
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

        self.mock_s3.start()
        self.client = boto3.client("s3")
        self.s3_bucket = self.client.create_bucket(Bucket=self.bucket_name)

        self.CREDENTIALS = Credentials.objects.create(
            username="test-username", role_arn="test-arn-arn-arn-arn"
        )
        self.bucket = Bucket.objects.create(name=self.bucket_name)

    def tearDown(self):
        self.mock_s3.stop()
        self.patcher.stop()

    def test_empty_sync(self):
        self.bucket.sync()
        assert self.generate_sts_buckets_credentials.call_count == 1
        assert self.bucket.object_set.count() == 0
        objects = self.client.list_objects_v2(Bucket=self.bucket_name).get(
            "Contents", []
        )
        assert len(objects) == 0
