import json
from unittest.mock import patch

import boto3
from django.test import override_settings
from moto import mock_aws

from hexa.core.test import TestCase
from hexa.plugins.connector_s3.api import (
    generate_download_url,
    generate_s3_policy,
    generate_sts_app_s3_credentials,
    generate_sts_user_s3_credentials,
    generate_upload_url,
)
from hexa.plugins.connector_s3.models import Bucket, Object

from .mocks.s3_credentials_mock import get_s3_mocked_env


@override_settings(**get_s3_mocked_env())
class ApiTest(TestCase):
    bucket_name = "test-bucket"

    def setUp(self):
        self.bucket = Bucket.objects.create(name=self.bucket_name)

    @mock_aws
    def test_generate_download_url(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="test.csv", Body="test")

        target_object = Object.objects.create(
            bucket=self.bucket, key="test.csv", size=100
        )

        self.assertIsInstance(
            generate_download_url(
                bucket=self.bucket,
                target_key=target_object.key,
            ),
            str,
        )

    @mock_aws
    def test_generate_upload_url(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        self.assertIsInstance(
            generate_upload_url(
                bucket=self.bucket,
                target_key="test.csv",
            ),
            str,
        )

    @mock_aws
    def test_generate_sts_app_s3_credentials(self):
        credentials = generate_sts_app_s3_credentials()
        self.assertIsInstance(credentials, dict)
        for key in ["AccessKeyId", "SecretAccessKey", "SessionToken"]:
            self.assertIsInstance(credentials[key], str)
            self.assertGreater(len(credentials[key]), 0)

    @mock_aws
    def test_generate_sts_app_s3_credentials_with_bucket(self):
        bucket = Bucket.objects.create(name="hexa-test-bucket")
        credentials = generate_sts_app_s3_credentials(bucket=bucket)
        self.assertIsInstance(credentials, dict)

    @mock_aws
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_generate_sts_app_team_credentials(self, _):
        bucket = Bucket.objects.create(name="hexa-test-bucket")
        credentials, _ = generate_sts_user_s3_credentials(
            role_identifier="test",
            session_identifier="test",
            read_write_buckets=[bucket],
            read_only_buckets=[],
        )
        self.assertIsInstance(credentials, dict)
        for key in ["AccessKeyId", "SecretAccessKey", "SessionToken"]:
            self.assertIsInstance(credentials[key], str)
            self.assertGreater(len(credentials[key]), 0)

    @mock_aws
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_generate_sts_app_team_credentials_long_ident(self, _):
        bucket = Bucket.objects.create(name="hexa-test-bucket")
        # activate hash mode for session name with a very long session identifier
        credentials, _ = generate_sts_user_s3_credentials(
            role_identifier="test",
            session_identifier="test",
            read_write_buckets=[bucket],
            read_only_buckets=[],
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
        buckets = [Bucket(name=f"hexa-test-bucket-name-{i}") for i in range(20)]
        policy = generate_s3_policy(read_write_buckets=buckets)
        self.assertIsInstance(policy, dict)
        self.assertLess(len(json.dumps(policy)), 2048)

    def test_generate_s3_policy_rw_ro(self):
        policy = generate_s3_policy(
            read_write_buckets=[Bucket(name="rw_bucket1"), Bucket(name="rw_bucket2")],
            read_only_buckets=[Bucket(name="ro_bucket1")],
        )

        expected_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "S3RO",
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket", "s3:GetObject"],
                    "Resource": [
                        "arn:aws:s3:::ro_bucket1",
                        "arn:aws:s3:::ro_bucket1/*",
                    ],
                },
                {
                    "Sid": "S3RWK",
                    "Effect": "Allow",
                    "Action": "s3:*Object",
                    "Resource": ["arn:aws:s3:::ro_bucket1/.s3keep"],
                },
                {
                    "Sid": "S3AllActions",
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket", "s3:*Object"],
                    "Resource": [
                        "arn:aws:s3:::rw_bucket1",
                        "arn:aws:s3:::rw_bucket2",
                        "arn:aws:s3:::rw_bucket1/*",
                        "arn:aws:s3:::rw_bucket2/*",
                    ],
                },
            ],
        }
        self.assertEqual(policy, expected_policy)
