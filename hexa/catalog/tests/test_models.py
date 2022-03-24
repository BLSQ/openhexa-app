from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from hexa.core.test import TestCase
from hexa.user_management.models import Membership, Team, User

from ..models import Index, IndexPermission


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
