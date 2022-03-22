import base64
import hashlib
import json
from unittest.mock import patch

import boto3
from moto import mock_iam, mock_sts

from hexa.core.test import TestCase
from hexa.notebooks.credentials import NotebooksCredentials
from hexa.pipelines.credentials import PipelinesCredentials
from hexa.pipelines.tests.test_credentials import BaseCredentialsTestCase
from hexa.plugins.connector_airflow.models import DAGAuthorizedDatasource
from hexa.plugins.connector_s3.api import parse_arn
from hexa.plugins.connector_s3.credentials import (
    notebooks_credentials,
    pipelines_credentials,
)
from hexa.plugins.connector_s3.models import Bucket, BucketPermission, Credentials
from hexa.user_management.models import Feature, FeatureFlag, Team, User


class NotebooksCredentialsTest(TestCase):
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
        cls.S3FS = Feature.objects.create(code="s3fs")

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

    @mock_iam
    @mock_sts
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_credentials_s3fs(self, _):
        """John is a regular user, should have access to 2 buckets"""

        FeatureFlag.objects.create(feature=self.S3FS, user=self.USER_JOHN)
        credentials = NotebooksCredentials(self.USER_JOHN)
        notebooks_credentials(credentials)
        self.assertEqual(credentials.env["HEXA_FEATURE_FLAG_S3FS"], "true")
        self.assertEqual("_PRIVATE_FUSE_CONFIG" in credentials.env, True)

        fuse_config = json.loads(
            base64.b64decode(credentials.env["_PRIVATE_FUSE_CONFIG"])
        )
        self.assertEqual("eu-central-1", fuse_config["aws_default_region"])
        self.assertIsInstance(fuse_config["access_key_id"], str)
        self.assertGreater(len(fuse_config["access_key_id"]), 0)
        self.assertIsInstance(fuse_config["secret_access_key"], str)
        self.assertGreater(len(fuse_config["secret_access_key"]), 0)
        self.assertIsInstance(fuse_config["session_token"], str)
        self.assertGreater(len(fuse_config["session_token"]), 0)
        for bucket_config in fuse_config["buckets"]:
            self.assertEqual("hexa-test-bucket-", bucket_config["name"][:17])
            self.assertEqual("eu-central-1", bucket_config["region"])
            self.assertEqual("RW", bucket_config["mode"])


class PipelinesCredentialsTest(BaseCredentialsTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.CREDENTIALS = Credentials.objects.create(
            username="hexa-app-test",
            access_key_id="foo",
            secret_access_key="bar",
            default_region="eu-central-1",
            user_arn="arn:aws:iam::111:user/hexa-app-unittest",
            app_role_arn="arn:aws:iam::222:role/hexa-app-unittest",
        )
        cls.BUCKET = Bucket.objects.create(name="hexa-test-bucket-1")

        cls.CLIENT = boto3.client(
            "iam",
            aws_access_key_id=cls.CREDENTIALS.access_key_id,
            aws_secret_access_key=cls.CREDENTIALS.secret_access_key,
        )

    @mock_iam
    @mock_sts
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_new_role(self, _):
        # Setup
        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.BUCKET
        )

        # Test
        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        # Check that we did create the role
        roles_data = self.CLIENT.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))

        expected_role_name = str(self.PIPELINE.id)
        self.assertEqual(expected_role_name, roles_data["Roles"][0]["RoleName"])

        expected_role_path = "/hexa-app-unittest/pipelines/connector_airflow/"
        self.assertEqual(expected_role_path, roles_data["Roles"][0]["Path"])

        # Check that the role has the correct policies
        policy_data = self.CLIENT.get_role_policy(
            RoleName=expected_role_name, PolicyName="s3-access"
        )
        self.assertEqual(
            policy_data["PolicyDocument"],
            {
                "Statement": [
                    {
                        "Action": "s3:*",
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

        self.assertEqual(
            {
                "AWS_DEFAULT_REGION": "eu-central-1",
                "AWS_S3_BUCKET_NAMES": "hexa-test-bucket-1",
            },
            credentials.env,
        )

    @mock_iam
    @mock_sts
    @patch("hexa.plugins.connector_s3.api.sleep", return_value=None)
    def test_existing_role(self, _):
        """
        When the role already exists, we should not create it again
        But the policy should be updated
        """

        # Setup
        self.CLIENT.create_role(
            Path="/hexa-app-unittest/pipelines/",
            RoleName=str(self.PIPELINE.id),
            AssumeRolePolicyDocument="some document",
        )

        DAGAuthorizedDatasource.objects.create(
            dag=self.PIPELINE, datasource=self.BUCKET
        )

        # Test
        credentials = PipelinesCredentials(self.PIPELINE)
        pipelines_credentials(credentials)

        # Check that we did not create a new role
        roles_data = self.CLIENT.list_roles()
        self.assertEqual(1, len(roles_data["Roles"]))

        # Check that the role has the correct policies
        expected_role_name = str(self.PIPELINE.id)
        policy_data = self.CLIENT.get_role_policy(
            RoleName=expected_role_name, PolicyName="s3-access"
        )
        self.assertEqual(
            policy_data["PolicyDocument"],
            {
                "Statement": [
                    {
                        "Action": "s3:*",
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

    @mock_iam
    @mock_sts
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

        self.assertEqual(
            {
                "AWS_DEFAULT_REGION": "eu-central-1",
                "AWS_S3_BUCKET_NAMES": "hexa-test-bucket-1",
                "AWS_BUCKET_SLUG1_NAME": "hexa-test-bucket-1",
            },
            credentials.env,
        )
