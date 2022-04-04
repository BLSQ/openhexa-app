import responses
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from hexa.core.test import TestCase
from hexa.user_management.models import Membership, MembershipRole, Team, User


class TeamTest(TestCase):
    USER_LUCY = None
    USER_SONNY = None
    USER_JIMMY = None
    DREAM_TEAM = None
    AVERAGE_TEAM = None

    @classmethod
    @responses.activate
    def setUpTestData(cls):
        cls.USER_LUCY = User.objects.create_user(
            "lucy@bluesquarehub.com",
            "lucylucy",
        )
        cls.USER_SONNY = User.objects.create_user(
            "sonny@bluesquarehub.com",
            "sonnysonny",
        )
        cls.USER_JIMMY = User.objects.create_user(
            "jimmy@bluesquarehub.com",
            "jimmityjim++",
        )
        cls.DREAM_TEAM = Team.objects.create(name="Dream Team")
        Membership.objects.create(
            user=cls.USER_LUCY, team=cls.DREAM_TEAM, role=MembershipRole.ADMIN
        )
        Membership.objects.create(
            user=cls.USER_SONNY, team=cls.DREAM_TEAM, role=MembershipRole.REGULAR
        )

    def test_add_user_to_team_principal_is_outside_team(self):
        with self.assertRaises(PermissionDenied):
            Team.objects.add_user_to_team(
                principal=self.USER_JIMMY, user=self.USER_JIMMY, team=self.DREAM_TEAM
            )

    def test_add_user_to_team_principal_is_not_admin(self):
        with self.assertRaises(PermissionDenied):
            Team.objects.add_user_to_team(
                principal=self.USER_SONNY, user=self.USER_JIMMY, team=self.DREAM_TEAM
            )

    def test_add_user_to_team_principal_is_admin(self):
        membership = Team.objects.add_user_to_team(
            principal=self.USER_LUCY, user=self.USER_JIMMY, team=self.DREAM_TEAM
        )
        self.assertIsInstance(membership, Membership)
        self.assertEqual(self.USER_JIMMY, membership.user)
        self.assertEqual(self.DREAM_TEAM, membership.team)
        self.assertEqual(MembershipRole.REGULAR, membership.role)

    def test_remove_user_from_team_principal_is_outside_team(self):
        with self.assertRaises(PermissionDenied):
            Team.objects.remove_user_from_team(
                principal=self.USER_JIMMY, user=self.USER_LUCY, team=self.DREAM_TEAM
            )

    def test_remove_user_from_team_principal_is_not_admin(self):
        with self.assertRaises(PermissionDenied):
            Team.objects.remove_user_from_team(
                principal=self.USER_SONNY, user=self.USER_LUCY, team=self.DREAM_TEAM
            )

    def test_remove_user_from_team_principal_is_admin(self):
        Team.objects.remove_user_from_team(
            principal=self.USER_LUCY, user=self.USER_SONNY, team=self.DREAM_TEAM
        )
        with self.assertRaises(ObjectDoesNotExist):
            Membership.objects.get(user=self.USER_SONNY, team=self.DREAM_TEAM)
