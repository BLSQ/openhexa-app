import boto3
from django.core.exceptions import ValidationError
from django.test import override_settings
from moto import mock_aws

from hexa.catalog.models import Index
from hexa.core.test import TestCase
from hexa.plugins.connector_s3.models import Bucket, BucketPermission, Object
from hexa.user_management.models import Membership, PermissionMode, Team, User

from .mocks.s3_credentials_mock import get_s3_mocked_env


@override_settings(**get_s3_mocked_env())
class ModelTest(TestCase):
    USER_JIM = None
    USER_JANE = None
    BUCKET_1 = None
    BUCKET_2 = None
    OBJECT_1 = None
    OBJECT_2 = None
    COLLECTION_MALARIA = None
    TEAM = None

    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_JIM = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimmytyjim",
            is_superuser=True,
        )
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janityjane",
            is_superuser=False,
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER_JANE)
        cls.BUCKET_1 = Bucket.objects.create(name="test-bucket-1")
        BucketPermission.objects.create(
            team=cls.TEAM, bucket=cls.BUCKET_1, mode=PermissionMode.EDITOR
        )
        cls.BUCKET_2 = Bucket.objects.create(name="test-bucket-2")
        BucketPermission.objects.create(
            team=cls.TEAM, bucket=cls.BUCKET_2, mode=PermissionMode.VIEWER
        )
        cls.OBJECT_1 = Object.objects.create(
            bucket=cls.BUCKET_2, key="file1.csv", size=100
        )
        cls.OBJECT_2 = Object.objects.create(
            bucket=cls.BUCKET_2, key="file2.csv", size=100
        )

    def test_filter_for_user_regular(self):
        self.assertEqual(
            [self.BUCKET_1, self.BUCKET_2],
            list(Bucket.objects.filter_for_user(self.USER_JANE)),
        )
        self.assertEqual(
            [self.BUCKET_1, self.BUCKET_2],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JANE,
                    mode__in=[PermissionMode.EDITOR, PermissionMode.VIEWER],
                )
            ),
        )
        self.assertEqual(
            [self.BUCKET_1],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JANE, mode=PermissionMode.EDITOR
                )
            ),
        )
        self.assertEqual(
            [self.BUCKET_2],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JANE, mode=PermissionMode.VIEWER
                )
            ),
        )
        self.assertEqual(
            [self.BUCKET_1],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JANE, mode__in=[PermissionMode.EDITOR]
                )
            ),
        )
        self.assertEqual(
            [self.BUCKET_2],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JANE, mode__in=[PermissionMode.VIEWER]
                )
            ),
        )

    def test_filter_for_user_superuser(self):
        self.assertEqual(
            [self.BUCKET_1, self.BUCKET_2],
            list(Bucket.objects.filter_for_user(self.USER_JIM)),
        )
        self.assertEqual(
            [self.BUCKET_1, self.BUCKET_2],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JIM,
                    mode__in=[PermissionMode.EDITOR, PermissionMode.VIEWER],
                )
            ),
        )
        self.assertEqual(
            [self.BUCKET_1, self.BUCKET_2],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JIM, mode=PermissionMode.EDITOR
                )
            ),
        )
        self.assertEqual(
            [],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JIM, mode=PermissionMode.VIEWER
                )
            ),
        )
        self.assertEqual(
            [self.BUCKET_1, self.BUCKET_2],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JIM, mode__in=[PermissionMode.EDITOR]
                )
            ),
        )
        self.assertEqual(
            [],
            list(
                Bucket.objects.filter_for_user(
                    self.USER_JIM, mode__in=[PermissionMode.VIEWER]
                )
            ),
        )

    def test_bucket_delete(self):
        """Deleting a bucket should delete its index as well"""
        bucket = Bucket.objects.create(name="some-bucket")
        bucket_id = bucket.id
        self.assertEqual(1, Index.objects.filter(object_id=bucket_id).count())
        bucket.delete()
        self.assertEqual(0, Index.objects.filter(object_id=bucket_id).count())

    @mock_aws
    def test_bucket_clean_ok(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="some-bucket")
        bucket = Bucket.objects.create(name="some-bucket")

        self.assertIsNone(bucket.clean())

    @mock_aws
    def test_bucket_clean_ko(self):
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="some-bucket")
        bucket = Bucket.objects.create(name="huh-wrong-bucket-name")

        with self.assertRaises(ValidationError):
            bucket.clean()


class PermissionTest(TestCase):
    USER_REGULAR = None
    TEAM_1 = None
    TEAM_2 = None
    BUCKET_1 = None
    BUCKET_2 = None

    @classmethod
    def setUpTestData(cls):
        cls.BUCKET_1_1 = Bucket.objects.create(name="aws_bucket1")
        cls.BUCKET_1_2 = Bucket.objects.create(name="aws_bucket2")
        cls.TEAM_1 = Team.objects.create(name="Test Team 1")
        cls.TEAM_2 = Team.objects.create(name="Test Team 2")
        BucketPermission.objects.create(bucket=cls.BUCKET_1_1, team=cls.TEAM_1)
        BucketPermission.objects.create(bucket=cls.BUCKET_1_1, team=cls.TEAM_2)
        cls.USER_REGULAR = User.objects.create_user(
            "jimbo@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM_1, user=cls.USER_REGULAR)
        Membership.objects.create(team=cls.TEAM_2, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "marylou@bluesquarehub.com",
            "super",
            is_superuser=True,
        )

        for bucket in [cls.BUCKET_1_1, cls.BUCKET_1_2]:
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


class PermissionTestWritableBy(TestCase):
    USER_REGULAR = None
    BUCKET_1 = None
    BUCKET_2 = None
    TEAM_1 = None
    TEAM_2 = None

    @classmethod
    def setUpTestData(cls):
        cls.BUCKET_1_1 = Bucket.objects.create(name="aws_bucket1")
        cls.BUCKET_1_2 = Bucket.objects.create(name="aws_bucket2")
        cls.TEAM_1 = Team.objects.create(name="Test Team1")
        cls.TEAM_2 = Team.objects.create(name="Test Team2")
        BucketPermission.objects.create(
            bucket=cls.BUCKET_1_1, team=cls.TEAM_1, mode=PermissionMode.VIEWER
        )
        BucketPermission.objects.create(
            bucket=cls.BUCKET_1_2, team=cls.TEAM_1, mode=PermissionMode.VIEWER
        )
        BucketPermission.objects.create(bucket=cls.BUCKET_1_1, team=cls.TEAM_2)
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )
        Membership.objects.create(team=cls.TEAM_1, user=cls.USER_REGULAR)
        Membership.objects.create(team=cls.TEAM_2, user=cls.USER_REGULAR)
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
            "super",
            is_superuser=True,
        )

    def test_bucket_writable(self):
        """
        - user super can write in bucket 1 and 2
        - user regular can write in bucket 1 (only one RO flag, RW flag via team 2 supersede)
        - user regular can't write in bucket 2
        """
        self.assertTrue(self.USER_SUPER.has_perm("connector_s3.write", self.BUCKET_1_1))
        self.assertTrue(self.USER_SUPER.has_perm("connector_s3.write", self.BUCKET_1_2))
        self.assertTrue(
            self.USER_REGULAR.has_perm("connector_s3.write", self.BUCKET_1_1)
        )
        self.assertFalse(
            self.USER_REGULAR.has_perm("connector_s3.write", self.BUCKET_1_2)
        )


class ConnectorS3PublicBucketTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bucket_priv = Bucket.objects.create(name="test-bucket-priv")
        cls.bucket_pub = Bucket.objects.create(name="test-bucket-pub", public=True)

    def test_objects_url(self):
        obj_priv = Object.objects.create(bucket=self.bucket_priv, key="hello", size=0)
        self.assertEqual(
            obj_priv.download_url, f"/s3/{self.bucket_priv.id}/object_download/hello/"
        )
        obj_pub = Object.objects.create(bucket=self.bucket_pub, key="hello", size=0)
        self.assertEqual(
            obj_pub.download_url,
            "https://test-bucket-pub.s3.eu-central-1.amazonaws.com/hello",
        )
