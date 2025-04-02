import base64
import hashlib
import json
from unittest.mock import patch

import boto3
from django.test import override_settings
from moto import mock_aws

from hexa.core.test import TestCase
from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.pipelines.tests.test_credentials import BaseCredentialsTestCase
from hexa.plugins.connector_airflow.models import DAGAuthorizedDatasource
from hexa.plugins.connector_s3.api import _get_app_s3_credentials, parse_arn
from hexa.plugins.connector_s3.credentials import (
    notebooks_credentials,
    pipelines_credentials,
)
from hexa.plugins.connector_s3.models import Bucket, BucketPermission
from hexa.user_management.models import (
    Membership,
    MembershipRole,
    PermissionMode,
    Team,
    User,
)

from .mocks.s3_credentials_mock import get_s3_mocked_env


@override_settings(**get_s3_mocked_env())
class NotebooksCredentialsTest(TestCase):
    USER_JANE = None
    USER_JOHN = None
    USER_WADE = None
    TEAM_HEXA = None
    TEAM_SECRET = None
    TEAM_ANNOYING = None
    CREDENTIALS = None

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
        cls.USER_WADE = User.objects.create_user(
            "wade@bluesquarehub.com",
            "waderocks999",
            is_superuser=False,
        )
        cls.TEAM_HEXA = Team.objects.create(name="Hexa Team!")
        cls.TEAM_ANNOYING = Team.objects.create(name="External Team!")
        cls.TEAM_SECRET = Team.objects.create(name="Annoying Team!")
        Membership.objects.create(
            user=cls.USER_JOHN, team=cls.TEAM_HEXA, role=MembershipRole.ADMIN
        )
        Membership.objects.create(
            user=cls.USER_JOHN, team=cls.TEAM_SECRET, role=MembershipRole.REGULAR
        )
        Membership.objects.create(
            user=cls.USER_WADE, team=cls.TEAM_ANNOYING, role=MembershipRole.REGULAR
        )
        cls.CREDENTIALS = _get_app_s3_credentials()
        b1 = Bucket.objects.create(name="hexa-test-bucket-1")
        b2 = Bucket.objects.create(name="hexa-test-bucket-2")
        Bucket.objects.create(name="hexa-test-bucket-3")
        BucketPermission.objects.create(
            bucket=b1, team=cls.TEAM_HEXA, mode=PermissionMode.VIEWER
        )
        BucketPermission.objects.create(bucket=b2, team=cls.TEAM_HEXA)
        BucketPermission.objects.create(
            bucket=b2, team=cls.TEAM_ANNOYING, mode=PermissionMode.VIEWER
        )
        BucketPermission.objects.create(
            bucket=b2, team=cls.TEAM_SECRET, mode=PermissionMode.VIEWER
        )

    @mock_aws
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_credentials(self, _):
        """John is a regular user, should have access to 2 buckets"""
        credentials = NotebooksCredentials(self.USER_JOHN)
        notebooks_credentials(credentials)
        aws_fuse_config = json.loads(
            base64.b64decode(credentials.env["AWS_S3_FUSE_CONFIG"])
        )
        self.assertEqual(
            "hexa-test-bucket-1,hexa-test-bucket-2",
            credentials.env["AWS_S3_BUCKET_NAMES"],
        )

        self.assertEqual(
            ["RO"],
            [
                b["mode"]
                for b in aws_fuse_config["buckets"]
                if b["name"] == "hexa-test-bucket-1"
            ],
        )
        self.assertEqual(
            ["RW"],
            [
                b["mode"]
                for b in aws_fuse_config["buckets"]
                if b["name"] == "hexa-test-bucket-2"
            ],
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
            aws_access_key_id=self.CREDENTIALS["access_key_id"],
            aws_secret_access_key=self.CREDENTIALS["secret_access_key"],
        )
        roles_data = iam_client.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))
        team_hash = hashlib.blake2s(
            ",".join(
                [str(t.id) for t in self.USER_JOHN.team_set.order_by("id")]
            ).encode("utf-8"),
            digest_size=16,
        ).hexdigest()
        expected_role_name = f"hexa-app-test-s3-{team_hash}"
        self.assertEqual(expected_role_name, roles_data["Roles"][0]["RoleName"])
        role_policies_data = iam_client.list_role_policies(RoleName=expected_role_name)
        self.assertEqual(1, len(role_policies_data["PolicyNames"]))
        self.assertEqual("s3-access", role_policies_data["PolicyNames"][0])

    @mock_aws
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
            aws_access_key_id=self.CREDENTIALS["access_key_id"],
            aws_secret_access_key=self.CREDENTIALS["secret_access_key"],
        )
        roles_data = iam_client.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))
        expected_role_name = "hexa-app-test-s3-superuser"
        self.assertEqual(expected_role_name, roles_data["Roles"][0]["RoleName"])
        role_policies_data = iam_client.list_role_policies(RoleName=expected_role_name)
        self.assertEqual(1, len(role_policies_data["PolicyNames"]))
        self.assertEqual("s3-access", role_policies_data["PolicyNames"][0])


@override_settings(**get_s3_mocked_env())
class PipelinesCredentialsTest(BaseCredentialsTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.CREDENTIALS = _get_app_s3_credentials()
        cls.BUCKET = Bucket.objects.create(name="hexa-test-bucket-1")

    @mock_aws
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_new_role(self, _):
        iam_client = boto3.client(
            "iam",
            aws_access_key_id=self.CREDENTIALS["access_key_id"],
            aws_secret_access_key=self.CREDENTIALS["secret_access_key"],
        )
        # Setup
        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.BUCKET
        )

        # Test
        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        # Check that we did create the role
        roles_data = iam_client.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))

        expected_role_name = "hexa-app-test-s3-p-" + str(self.PIPELINE.id)
        self.assertEqual(expected_role_name, roles_data["Roles"][0]["RoleName"])
        self.assertEqual("/", roles_data["Roles"][0]["Path"])

        # Check that the role has the correct policies
        policy_data = iam_client.get_role_policy(
            RoleName=expected_role_name, PolicyName="s3-access"
        )
        self.assertEqual(
            policy_data["PolicyDocument"],
            {
                "Statement": [
                    {
                        "Action": ["s3:ListBucket", "s3:*Object"],
                        "Effect": "Allow",
                        "Resource": [
                            "arn:aws:s3:::hexa-test-bucket-1",
                            "arn:aws:s3:::hexa-test-bucket-1/*",
                        ],
                        "Sid": "S3AllActions",
                    }
                ],
                "Version": "2012-10-17",
            },
        )

        # Check that the STS credentials belong to the correct role
        client = boto3.client(
            "sts",
            aws_access_key_id=credentials.env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=credentials.env["AWS_SECRET_ACCESS_KEY"],
        )
        response = client.get_caller_identity()

        self.assertEqual(
            parse_arn(response["Arn"])["resource"].split("/")[0], expected_role_name
        )

        # Check that we do send the correct env variables
        for key in [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
        ]:
            self.assertIsInstance(credentials.env[key], str)
            self.assertGreater(len(credentials.env[key]), 0)
            del credentials.env[key]

        # opaque content in base64
        self.assertTrue("AWS_S3_FUSE_CONFIG" in credentials.env)
        aws_fuse_config = json.loads(
            base64.b64decode(credentials.env["AWS_S3_FUSE_CONFIG"])
        )
        for key in [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
        ]:
            self.assertIsInstance(aws_fuse_config[key], str)
            self.assertGreater(len(aws_fuse_config[key]), 0)
        del credentials.env["AWS_S3_FUSE_CONFIG"]

        self.assertEqual(
            {
                "AWS_DEFAULT_REGION": "eu-central-1",
                "AWS_S3_BUCKET_NAMES": "hexa-test-bucket-1",
                "AWS_FRESH_ROLE": "TRUE",
            },
            credentials.env,
        )

    @mock_aws
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_existing_role(self, _):
        """
        When the role already exists, we should not create it again
        But the policy should be updated
        """
        iam_client = boto3.client(
            "iam",
            aws_access_key_id=self.CREDENTIALS["access_key_id"],
            aws_secret_access_key=self.CREDENTIALS["secret_access_key"],
        )
        # Setup
        iam_client.create_role(
            Path="/hexa-app-unittest/pipelines/",
            RoleName="hexa-app-test-s3-p-" + str(self.PIPELINE.id),
            AssumeRolePolicyDocument="some document",
        )

        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.BUCKET
        )

        # Test
        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        # Check that we did not create a new role
        roles_data = iam_client.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))

        # Check that the role has the correct policies
        expected_role_name = "hexa-app-test-s3-p-" + str(self.PIPELINE.id)
        policy_data = iam_client.get_role_policy(
            RoleName=expected_role_name, PolicyName="s3-access"
        )
        self.assertEqual(
            policy_data["PolicyDocument"],
            {
                "Statement": [
                    {
                        "Action": ["s3:ListBucket", "s3:*Object"],
                        "Effect": "Allow",
                        "Resource": [
                            "arn:aws:s3:::hexa-test-bucket-1",
                            "arn:aws:s3:::hexa-test-bucket-1/*",
                        ],
                        "Sid": "S3AllActions",
                    }
                ],
                "Version": "2012-10-17",
            },
        )

        # Check that the STS credentials belong to the correct role
        client = boto3.client(
            "sts",
            aws_access_key_id=credentials.env["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=credentials.env["AWS_SECRET_ACCESS_KEY"],
        )
        response = client.get_caller_identity()

        self.assertEqual(
            parse_arn(response["Arn"])["resource"].split("/")[0], expected_role_name
        )

    @mock_aws
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_slug(self, _):
        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.BUCKET, slug="slug1"
        )

        # Test
        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        # Validate
        for key in [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
        ]:
            self.assertIsInstance(credentials.env[key], str)
            self.assertGreater(len(credentials.env[key]), 0)
            del credentials.env[key]

        # opaque content in base64
        self.assertTrue("AWS_S3_FUSE_CONFIG" in credentials.env)
        aws_fuse_config = json.loads(
            base64.b64decode(credentials.env["AWS_S3_FUSE_CONFIG"])
        )
        for key in [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
        ]:
            self.assertIsInstance(aws_fuse_config[key], str)
            self.assertGreater(len(aws_fuse_config[key]), 0)
        del credentials.env["AWS_S3_FUSE_CONFIG"]

        self.assertEqual(
            {
                "AWS_DEFAULT_REGION": "eu-central-1",
                "AWS_S3_BUCKET_NAMES": "hexa-test-bucket-1",
                "AWS_BUCKET_SLUG1_NAME": "hexa-test-bucket-1",
                "AWS_FRESH_ROLE": "TRUE",
            },
            credentials.env,
        )
