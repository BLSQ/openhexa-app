import responses

from hexa.core.test import TestCase
from hexa.user_management.models import Membership, Team, User


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
        pass

    def test_membership_create_from_user_outside_team_2(self):
        pass
