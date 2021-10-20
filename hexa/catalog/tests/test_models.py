from django import test
from django.contrib.contenttypes.models import ContentType

from hexa.user_management.models import Membership, Team, User

from ..models import Index, IndexPermission


class PermissionTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "regular",
        )
        cls.USER_SUPER = User.objects.create_user(
            "mary@bluesquarehub.com",
            "super",
            is_superuser=True,
        )
        cls.TEAM1 = Team.objects.create(name="Test Team1")
        cls.TEAM2 = Team.objects.create(name="Test Team2")
        Membership.objects.create(team=cls.TEAM1, user=cls.USER_REGULAR)
        Membership.objects.create(team=cls.TEAM2, user=cls.USER_REGULAR)

        # index over users. dont mind the object_id, it should not have any impact
        ct = ContentType.objects.filter(
            app_label="user_management", model="user"
        ).first()
        cls.I1 = Index.objects.create(content_type=ct, object_id=cls.USER_SUPER.id)
        cls.I2 = Index.objects.create(content_type=ct, object_id=cls.USER_REGULAR.id)
        IndexPermission.objects.create(index=cls.I1, team=cls.TEAM1)
        IndexPermission.objects.create(index=cls.I1, team=cls.TEAM2)

    def test_instance_dedup(self):
        """
        - user super see 2 indexes (all of them)
        - user regular see only 1 index, one time
        """
        self.assertEqual(
            list(
                Index.objects.filter_for_user(self.USER_REGULAR)
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
                    {"object_id": self.USER_REGULAR.id},
                    {"object_id": self.USER_SUPER.id},
                ],
                key=lambda o: o["object_id"],
            ),
        )
