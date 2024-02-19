from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from hexa.core.test import TestCase
from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Membership,
    MembershipRole,
    Team,
    User,
)


class ModelsTest(TestCase):
    USER_SERENA = None
    USER_JOE = None
    USER_GREG = None
    USER_PETE = None
    TEAM_1 = None
    TEAM_2 = None
    MEMBERSHIP_SERENA = None
    MEMBERSHIP_GREG = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )
        cls.USER_JOE = User.objects.create_user(
            "joe@bluesquarehub.com",
            "joe's password",
        )
        cls.USER_GREG = User.objects.create_user(
            "greg@bluesquarehub.com",
            "greg's password",
        )
        cls.USER_PETE = User.objects.create_user(
            "pete@bluesquarehub.com", "pete's password", is_superuser=True
        )
        cls.TEAM_1 = Team.objects.create(name="A team")
        cls.MEMBERSHIP_SERENA = Membership.objects.create(
            user=cls.USER_SERENA, team=cls.TEAM_1, role=MembershipRole.ADMIN
        )
        cls.MEMBERSHIP_GREG = Membership.objects.create(
            user=cls.USER_GREG, team=cls.TEAM_1, role=MembershipRole.REGULAR
        )
        cls.TEAM_2 = Team.objects.create(name="Another team")

    def test_initials_no_first_and_last_name(self):
        """Users without first/last names should have the first two letters of their username as initials"""
        user = User(email="plop@openhexa.org")
        self.assertEqual("PL", user.initials)

    def test_initials_with_first_and_last_name(self):
        """Users with a first and last name should have initials composed of the first letter of both names"""
        user = User(email="plop@openhexa.org", first_name="John", last_name="Doe")
        self.assertEqual("JD", user.initials)

    def test_has_feature_flag(self):
        user = User.objects.create_user(
            email="plop@openhexa.org",
            first_name="John",
            last_name="Doe",
            password="ablackcat",
        )
        feature = Feature.objects.create(code="feature_1")
        FeatureFlag.objects.create(user=user, feature=feature)

        self.assertTrue(user.has_feature_flag("feature_1"))
        self.assertFalse(user.has_feature_flag("feature_2"))

    def test_forced_feature_flag(self):
        user = User.objects.create_user(
            email="plop@openhexa.org",
            first_name="John",
            last_name="Doe",
            password="ablackcat",
        )
        Feature.objects.create(code="feature_2", force_activate=True)
        Feature.objects.create(code="feature_3", force_activate=False)

        self.assertTrue(user.has_feature_flag("feature_2"))
        self.assertFalse(user.has_feature_flag("feature_3"))

    def test_team_create(self):
        new_team = Team.objects.create_if_has_perm(self.USER_JOE, name="Joe's team")
        self.assertIsInstance(new_team, Team)
        self.assertTrue(
            Membership.objects.filter(
                user=self.USER_JOE, team=new_team, role=MembershipRole.ADMIN
            ).exists()
        )

    def test_team_update_not_owner(self):
        with self.assertRaises(PermissionDenied):
            self.TEAM_1.update_if_has_perm(self.USER_GREG, name="Yolo team")

    def test_team_update(self):
        self.TEAM_1.update_if_has_perm(self.USER_SERENA, name="Updated team")
        self.TEAM_1.refresh_from_db()
        self.assertEqual("Updated team", self.TEAM_1.name)

    def test_team_delete_not_owner(self):
        with self.assertRaises(PermissionDenied):
            self.TEAM_1.delete_if_has_perm(self.USER_GREG)

    def test_team_delete(self):
        self.TEAM_1.delete_if_has_perm(self.USER_SERENA)
        with self.assertRaises(ObjectDoesNotExist):
            Team.objects.get(id=self.TEAM_1.id)

    def test_membership_create_if_has_perm(self):
        # Nice try, Joe
        with self.assertRaises(PermissionDenied):
            Membership.objects.create_if_has_perm(
                self.USER_JOE,
                user=self.USER_JOE,
                team=self.TEAM_1,
                role=MembershipRole.ADMIN,
            )

        membership = Membership.objects.create_if_has_perm(
            self.USER_SERENA, user=self.USER_JOE, team=self.TEAM_1
        )
        self.assertIsInstance(membership, Membership)
        self.assertEqual(self.USER_JOE, membership.user)
        self.assertEqual(self.TEAM_1, membership.team)
        self.assertEqual(MembershipRole.REGULAR, membership.role)

    def test_membership_update_if_has_perm(self):
        # Nice try, Greg
        with self.assertRaises(PermissionDenied):
            self.MEMBERSHIP_GREG.update_if_has_perm(
                self.USER_GREG, role=MembershipRole.ADMIN
            )

        self.MEMBERSHIP_GREG.update_if_has_perm(
            self.USER_SERENA, role=MembershipRole.ADMIN
        )
        self.MEMBERSHIP_GREG.refresh_from_db()
        self.assertEqual(MembershipRole.ADMIN, self.MEMBERSHIP_GREG.role)

    def test_membership_delete_if_has_perm(self):
        with self.assertRaises(PermissionDenied):
            self.MEMBERSHIP_SERENA.delete_if_has_perm(self.USER_GREG)

        self.MEMBERSHIP_GREG.delete_if_has_perm(self.USER_SERENA)
        self.assertFalse(
            Membership.objects.filter(user=self.USER_GREG, team=self.TEAM_1).exists()
        )

    def test_filter_for_user(self):
        teams = Team.objects.filter_for_user(self.USER_SERENA)
        self.assertEqual(1, len(teams))
        self.assertIn(self.TEAM_1, teams)

    def test_filter_for_superuser(self):
        teams = Team.objects.filter_for_user(self.USER_PETE)
        self.assertEqual(2, len(teams))
        self.assertIn(self.TEAM_1, teams)
        self.assertIn(self.TEAM_2, teams)
