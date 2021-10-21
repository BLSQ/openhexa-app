import hashlib
from unittest.mock import patch

import boto3
from django import test
from moto import mock_iam, mock_sts

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_s3.credentials import notebooks_credentials
from hexa.plugins.connector_s3.models import Bucket, BucketPermission, Credentials
from hexa.user_management.models import Team, User


class CredentialsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )
        cls.USER_JOHN = User.objects.create_user(
            "john@bluesquarehub.com",
            "johnrocks999",
            is_superuser=False,
        )
        cls.TEAM_HEXA = Team.objects.create(name="Hexa Team!")
        cls.USER_JOHN.team_set.add(cls.TEAM_HEXA)
        cls.CREDENTIALS = Credentials.objects.create(
            username="hexa-app-test",
            access_key_id="foo",
            secret_access_key="bar",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        b1 = Bucket.objects.create(name="hexa-test-bucket-1")
        b2 = Bucket.objects.create(name="hexa-test-bucket-2")
        Bucket.objects.create(name="hexa-test-bucket-3")
        BucketPermission.objects.create(bucket=b1, team=cls.TEAM_HEXA)
        BucketPermission.objects.create(bucket=b2, team=cls.TEAM_HEXA)

    @mock_iam
    @mock_sts
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_credentials(self, _):
        """John is a regular user, should have access to 2 buckets"""

        credentials = NotebooksCredentials(self.USER_JOHN)
        notebooks_credentials(credentials)
        self.assertEqual("false", credentials.env["HEXA_FEATURE_FLAG_S3FS"])
        self.assertEqual(
            "hexa-test-bucket-1,hexa-test-bucket-2",
            credentials.env["AWS_S3_BUCKET_NAMES"],
        )
        for key in [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "AWS_DEFAULT_REGION",
        ]:
            self.assertIsInstance(credentials.env[key], str)
            self.assertGreater(len(credentials.env[key]), 0)

        iam_client = boto3.client(
            "iam",
            aws_access_key_id=self.CREDENTIALS.access_key_id,
            aws_secret_access_key=self.CREDENTIALS.secret_access_key,
        )
        roles_data = iam_client.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))
        team_hash = hashlib.blake2s(
            str(self.TEAM_HEXA.id).encode("utf-8"), digest_size=16
        ).hexdigest()
        expected_role_name = f"hexa-app-test-s3-{team_hash}"
        self.assertEqual(expected_role_name, roles_data["Roles"][0]["RoleName"])
        role_policies_data = iam_client.list_role_policies(RoleName=expected_role_name)
        self.assertEqual(1, len(role_policies_data["PolicyNames"]))
        self.assertEqual("s3-access", role_policies_data["PolicyNames"][0])

    @mock_iam
    @mock_sts
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_credentials_superuser(self, _):
        """Jane is a superuser, should have access to 3 buckets"""

        credentials = NotebooksCredentials(self.USER_JANE)
        notebooks_credentials(credentials)
        self.assertEqual(
            "hexa-test-bucket-1,hexa-test-bucket-2,hexa-test-bucket-3",
            credentials.env["AWS_S3_BUCKET_NAMES"],
        )

        iam_client = boto3.client(
            "iam",
            aws_access_key_id=self.CREDENTIALS.access_key_id,
            aws_secret_access_key=self.CREDENTIALS.secret_access_key,
        )
        roles_data = iam_client.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))
        expected_role_name = "hexa-app-test-s3-superuser"
        self.assertEqual(expected_role_name, roles_data["Roles"][0]["RoleName"])
        role_policies_data = iam_client.list_role_policies(RoleName=expected_role_name)
        self.assertEqual(1, len(role_policies_data["PolicyNames"]))
        self.assertEqual("s3-access", role_policies_data["PolicyNames"][0])
