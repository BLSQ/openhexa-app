import json
from unittest.mock import patch

import boto3
from django import test
from moto import mock_iam, mock_s3, mock_sts

from hexa.plugins.connector_s3.api import (
    generate_download_url,
    generate_s3_policy,
    generate_sts_app_s3_credentials,
    generate_sts_user_s3_credentials,
    generate_upload_url,
)
from hexa.plugins.connector_s3.models import Bucket, Credentials, Object


class ApiTest(test.TestCase):
    bucket_name = "test-bucket"

    def setUp(self):
        self.credentials = Credentials.objects.create(
            username="test-username",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
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

    @mock_sts
    def test_generate_sts_app_s3_credentials(self):
        principal_credentials = Credentials.objects.create(
            username="hexa-app-test",
            access_key_id="foo",
            secret_access_key="bar",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        credentials = generate_sts_app_s3_credentials(
            principal_credentials=principal_credentials
        )
        self.assertIsInstance(credentials, dict)
        for key in ["AccessKeyId", "SecretAccessKey", "SessionToken"]:
            self.assertIsInstance(credentials[key], str)
            self.assertGreater(len(credentials[key]), 0)

    @mock_sts
    def test_generate_sts_app_s3_credentials_with_bucket(self):
        principal_credentials = Credentials.objects.create(
            username="hexa-app-test",
            access_key_id="bar",
            secret_access_key="baz",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        bucket = Bucket.objects.create(name="hexa-test-bucket")
        credentials = generate_sts_app_s3_credentials(
            principal_credentials=principal_credentials, bucket=bucket
        )
        self.assertIsInstance(credentials, dict)

    @mock_iam
    @mock_sts
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_generate_sts_app_team_credentials(self, _):
        bucket = Bucket.objects.create(name="hexa-test-bucket")
        principal_credentials = Credentials.objects.create(
            username="hexa-app-test",
            access_key_id="foo",
            secret_access_key="bar",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        credentials = generate_sts_user_s3_credentials(
            session_identifier="test",
            role_identifier="test",
            principal_credentials=principal_credentials,
            buckets=[bucket],
        )
        self.assertIsInstance(credentials, dict)
        for key in ["AccessKeyId", "SecretAccessKey", "SessionToken"]:
            self.assertIsInstance(credentials[key], str)
            self.assertGreater(len(credentials[key]), 0)

    def test_generate_s3_policy(self):
        """STS policies are limited to 2048 characters.
        Let's check that we can at least handle 20 buckets with medium-length names
        (see https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html)
        """

        bucket_names = [f"hexa-test-bucket-name-{i}" for i in range(20)]
        policy = generate_s3_policy(bucket_names)
        self.assertIsInstance(policy, dict)
        self.assertLess(len(json.dumps(policy)), 2048)
