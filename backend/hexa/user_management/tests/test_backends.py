from django.contrib.auth.models import Permission

from hexa.core.test import TestCase
from hexa.user_management.backends import PermissionsBackend
from hexa.user_management.models import Membership, MembershipRole, Team, User


class PermissionsBackendTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ADMIN = User.objects.create_user("julia@bluesquarehub.com", "password")
        cls.TEAM = Team.objects.create(name="Test team")
        Membership.objects.create(
            user=cls.ADMIN, team=cls.TEAM, role=MembershipRole.ADMIN
        )
        cls.backend = PermissionsBackend()

    def test_hexa_app_permission_without_object(self):
        self.assertTrue(
            self.backend.has_perm(self.ADMIN, "user_management.create_team")
        )

    def test_hexa_app_permission_with_object(self):
        self.assertTrue(
            self.backend.has_perm(self.ADMIN, "user_management.update_team", self.TEAM)
        )

    def test_unknown_permission_in_hexa_app_raises(self):
        with self.assertRaises(AttributeError):
            self.backend.has_perm(self.ADMIN, "user_management.not_a_permission")

    def test_non_hexa_app_permission_returns_false(self):
        """Regression test: permissions of third-party apps (e.g. django_sql_dashboard)
        must be delegated to other backends instead of raising ValueError.
        """
        self.assertFalse(
            self.backend.has_perm(self.ADMIN, "django_sql_dashboard.execute_sql")
        )

    def test_unknown_app_label_returns_false(self):
        self.assertFalse(self.backend.has_perm(self.ADMIN, "nonexistent_app.do_stuff"))

    def test_permission_without_app_label_returns_false(self):
        self.assertFalse(self.backend.has_perm(self.ADMIN, "no_dot_permission"))

    def test_third_party_permission_falls_through_to_model_backend(self):
        """The backend resolves third-party app permissions via Django's ModelBackend
        without blowing up.
        """
        self.assertFalse(self.ADMIN.has_perm("django_sql_dashboard.execute_sql"))

        permission = Permission.objects.get(
            codename="execute_sql",
            content_type__app_label="django_sql_dashboard",
        )
        self.ADMIN.user_permissions.add(permission)
        # Re-fetch to clear ModelBackend's per-instance permission cache
        user = User.objects.get(pk=self.ADMIN.pk)
        self.assertTrue(user.has_perm("django_sql_dashboard.execute_sql"))
