import responses
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from hexa.core.test import TestCase
from hexa.user_management.models import Membership, MembershipRole, Team, User


class TeamTest(TestCase):
    USER_SONNY = None
    USER_LUCY = None
    DREAM_TEAM = None
    AVERAGE_TEAM = None

    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_SONNY = User.objects.create_user(
            "sonny@bluesquarehub.com",
            "sonnysonny",
        )
        cls.USER_LUCY = User.objects.create_user(
            "lucy@bluesquarehub.com",
            "lucylucy",
        )
        cls.DREAM_TEAM = Team.objects.create(name="Dream Team")
        cls.AVERAGE_TEAM = Team.objects.create(name="Average Team")
        Membership.objects.create(user=cls.USER_SONNY, team=cls.AVERAGE_TEAM)
        Membership.objects.create(user=cls.USER_LUCY, team=cls.DREAM_TEAM)

    def test_membership_create_from_user_outside_team_1(self):
        with self.assertRaises(PermissionDenied):
            Team.objects.if_user_has_perm(
                self.USER_SONNY,
                "user_management.creat.create_project_in_team",
                self.DREAM_TEAM,
            ).add_user_to_team(
                user=self.USER_SONNY,
                team=self.DREAM_TEAM,
                role=MembershipRole.ADMIN,  # Nice try, Sonny!
            )

    def test_membership_create_from_user_outside_team_2(self):
        with self.assertRaises(ObjectDoesNotExist):
            Team.objects.filter_for_user(
                self.USER_SONNY,
                role=MembershipRole.ADMIN,
            ).get(id=self.DREAM_TEAM.id).add_user(
                self.USER_SONNY, role=MembershipRole.ADMIN  # Nice try, Sonny!
            )
