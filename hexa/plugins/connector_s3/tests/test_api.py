import boto3
from django import test
from moto import mock_s3, mock_sts

from hexa.plugins.connector_s3.api import generate_download_url, generate_upload_url
from hexa.plugins.connector_s3.models import Bucket, Credentials, Object


class ApiTest(test.TestCase):
    bucket_name = "test-bucket"

    def setUp(self):
        self.credentials = Credentials.objects.create(
            username="test-username",
            role_arn="test-arn-arn-arn-arn",
            default_region="eu-central-1",
        )
        self.bucket = Bucket.objects.create(name=self.bucket_name)

    @mock_s3
    @mock_sts
    def test_generate_download_url(self):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="test.csv", Body="test")

        target_object = Object.objects.create(
            bucket=self.bucket, key="test.csv", size=100
        )

        self.assertIsInstance(
            generate_download_url(
                principal_credentials=self.credentials,
                bucket=self.bucket,
                target_object=target_object,
            ),
            str,
        )

    @mock_s3
    @mock_sts
    def test_generate_upload_url(self):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket="test-bucket")
        self.assertIsInstance(
            generate_upload_url(
                principal_credentials=self.credentials,
                bucket=self.bucket,
                target_key="test.csv",
            ),
            str,
        )
