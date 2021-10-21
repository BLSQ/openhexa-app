from unittest import skip

import boto3
from django import test
from django.core.exceptions import ValidationError
from django.urls import reverse
from moto import mock_s3, mock_sts

from hexa.catalog.models import Index
from hexa.plugins.connector_s3.models import (
    Bucket,
    BucketPermission,
    Credentials,
    Object,
)
from hexa.user_management.models import Membership, Team, User


class ConnectorS3Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.team = Team.objects.create(name="Test Team")
        cls.user_jim = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )
        Membership.objects.create(team=cls.team, user=cls.user_jim)
        cls.api_credentials = Credentials.objects.create(
            username="app-iam-username",
            access_key_id="FOO",
            secret_access_key="BAR",
            default_region="us-west-2",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        cls.bucket = Bucket.objects.create(name="test-bucket")
        BucketPermission.objects.create(team=cls.team, bucket=cls.bucket)

    @skip("Deactivated for now - mocks needed")
    def test_credentials_200(self):
        self.client.login(email="jim@bluesquarehub.com", password="regular")
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("username", response_data)
        self.assertEqual("jim@bluesquarehub.com", response_data["username"])
        self.assertIn("env", response_data)
        self.assertEqual(
            {
                "S3_TEST_bucket_bucket_NAME": "test-bucket",
                "S3_TEST_bucket_ACCESS_KEY_ID": "FOO",
                "S3_TEST_bucket_SECRET_ACCESS_KEY": "BAR",
            },
            response_data["env"],
        )

    def test_bucket_delete(self):
        """Deleting a bucket should delete its index as well"""

        bucket = Bucket.objects.create(name="some-bucket")
        bucket_id = bucket.id
        self.assertEqual(1, Index.objects.filter(object_id=bucket_id).count())
        bucket.delete()
        self.assertEqual(0, Index.objects.filter(object_id=bucket_id).count())

    @mock_s3
    @mock_sts
    def test_bucket_clean_ok(self):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket="some-bucket")
        bucket = Bucket.objects.create(name="some-bucket")

        self.assertIsNone(bucket.clean())

    @mock_s3
    @mock_sts
    def test_bucket_clean_ko(self):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket="some-bucket")
        bucket = Bucket.objects.create(name="huh-wrong-bucket-name")

        with self.assertRaises(ValidationError):
            bucket.clean()


class PermissionTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.BUCKET1 = Bucket.objects.create(name="aws_bucket1")
        cls.BUCKET2 = Bucket.objects.create(name="aws_bucket2")
        cls.TEAM1 = Team.objects.create(name="Test Team1")
        cls.TEAM2 = Team.objects.create(name="Test Team2")
        BucketPermission.objects.create(bucket=cls.BUCKET1, team=cls.TEAM1)
        BucketPermission.objects.create(bucket=cls.BUCKET1, team=cls.TEAM2)
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM1, user=cls.USER_REGULAR)
        Membership.objects.create(team=cls.TEAM2, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
            "super",
            is_superuser=True,
        )

        for bucket in [cls.BUCKET1, cls.BUCKET2]:
            for i in range(2):
                Object.objects.create(
                    bucket=bucket, key=f"object-{bucket.name}-{i}", size=100
                )

    def test_bucket_dedup(self):
        """
        - user super see 2 buckets (all of them)
        - user regular see only bucket 1, one time
        """
        self.assertEqual(
            list(
                Bucket.objects.filter_for_user(self.USER_REGULAR)
                .order_by("name")
                .values("name")
            ),
            [{"name": "aws_bucket1"}],
        )
        self.assertEqual(
            list(
                Bucket.objects.filter_for_user(self.USER_SUPER)
                .order_by("name")
                .values("name")
            ),
            [{"name": "aws_bucket1"}, {"name": "aws_bucket2"}],
        )

    def test_objects_dedup(self):
        """
        regular user can see 2 objects
        super user can see 4 objects
        """
        self.assertEqual(
            list(
                Object.objects.filter_for_user(self.USER_REGULAR)
                .order_by("key")
                .values("key")
            ),
            [{"key": "object-aws_bucket1-0"}, {"key": "object-aws_bucket1-1"}],
        )
        self.assertEqual(
            list(
                Object.objects.filter_for_user(self.USER_SUPER)
                .order_by("key")
                .values("key")
            ),
            [
                {"key": "object-aws_bucket1-0"},
                {"key": "object-aws_bucket1-1"},
                {"key": "object-aws_bucket2-0"},
                {"key": "object-aws_bucket2-1"},
            ],
        )
