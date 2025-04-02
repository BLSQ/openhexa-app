import boto3
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings
from moto import mock_aws

from hexa.core.test import TestCase
from hexa.plugins.connector_s3.models import Bucket, BucketPermission
from hexa.plugins.connector_s3.tests.mocks.s3_credentials_mock import get_s3_mocked_env
from hexa.user_management.models import Membership, Team, User

from ..models import Index, IndexPermission
from ..queue import datasource_work_queue


class PermissionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimmyjim",
        )
        cls.USER_REGULAR_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janyjane",
        )
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
            "super",
            is_superuser=True,
        )
        cls.TEAM1 = Team.objects.create(name="Test Team1")
        cls.TEAM2 = Team.objects.create(name="Test Team2")
        Membership.objects.create(team=cls.TEAM1, user=cls.USER_REGULAR_1)
        Membership.objects.create(team=cls.TEAM2, user=cls.USER_REGULAR_1)

        # index over users. dont mind the object_id, it should not have any impact
        cls.CT = ContentType.objects.filter(
            app_label="user_management", model="user"
        ).first()
        cls.I1 = Index.objects.create(content_type=cls.CT, object_id=cls.USER_SUPER.id)
        cls.I2 = Index.objects.create(
            content_type=cls.CT, object_id=cls.USER_REGULAR_1.id
        )
        IndexPermission.objects.create(index=cls.I1, team=cls.TEAM1)
        IndexPermission.objects.create(index=cls.I1, team=cls.TEAM2)

    def test_instance_dedup(self):
        """
        - user super see 2 indexes (all of them)
        - user regular see only 1 index, one time
        """
        self.assertEqual(
            list(
                Index.objects.filter_for_user(self.USER_REGULAR_1)
                .order_by("object_id")
                .values("object_id")
            ),
            [{"object_id": self.USER_SUPER.id}],
        )
        self.assertEqual(
            list(
                Index.objects.filter_for_user(self.USER_SUPER)
                .order_by("object_id")
                .values("object_id")
            ),
            sorted(
                [
                    {"object_id": self.USER_REGULAR_1.id},
                    {"object_id": self.USER_SUPER.id},
                ],
                key=lambda o: o["object_id"],
            ),
        )

    def test_filter_for_user(self):
        index = Index.objects.create(content_type=self.CT, object_id=self.USER_SUPER.id)
        IndexPermission.objects.create(index=index, team=self.TEAM1)
        self.assertEqual(
            index, Index.objects.filter_for_user(self.USER_REGULAR_1).get(id=index.id)
        )
        with self.assertRaises(ObjectDoesNotExist):
            Index.objects.filter_for_user(self.USER_REGULAR_2).get(id=index.id)


@override_settings(**get_s3_mocked_env())
class PermissionUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimmyjim",
        )
        cls.USER_REGULAR_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janyjane",
        )
        cls.TEAM1 = Team.objects.create(name="Test Team1")
        cls.TEAM2 = Team.objects.create(name="Test Team2")
        Membership.objects.create(team=cls.TEAM1, user=cls.USER_REGULAR_1)
        Membership.objects.create(team=cls.TEAM2, user=cls.USER_REGULAR_2)
        cls.BUCKET = Bucket.objects.create(name="test-bucket")

    @mock_aws
    def test_permission_update(self):
        # we start the test with one index: the bucket
        self.assertEqual(Index.objects.count(), 1)

        # let's make a bucket with two files
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="file1", Body="test")
        s3_client.put_object(Bucket="test-bucket", Key="file2", Body="test")
        self.BUCKET.sync()

        # do we have 2 things in the bucket?
        self.assertEqual(Index.objects.count(), 3)

        # USER1/USER2 dont see anything
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_1).count(), 0)
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_2).count(), 0)

        # add permission between team 1 and bucket
        bp = BucketPermission.objects.create(bucket=self.BUCKET, team=self.TEAM1)

        # USER1 see the bucket but not object, index permission not updated
        # USER2 dont see anything
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_1).count(), 1)
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_2).count(), 0)

        # update permission async
        while datasource_work_queue.run_once():
            pass

        # USER1 see the 3 indexes, but not USER2
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_1).count(), 3)
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_2).count(), 0)

        # update permission: now bucket perm is the same but between team2 and bucket!
        bp.team = self.TEAM2
        bp.save()
        while datasource_work_queue.run_once():
            pass

        # USER1 dont see anything, USER2 see DS + objects
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_1).count(), 0)
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_2).count(), 3)

        # remove permission and update index permission
        bp.delete()
        while datasource_work_queue.run_once():
            pass

        # USER1/USER2 dont see anything
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_1).count(), 0)
        self.assertEqual(Index.objects.filter_for_user(self.USER_REGULAR_2).count(), 0)
