import responses
from django.conf import settings
from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import Feature, User


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )

    def test_any_page_anonymous_302(self):
        response = self.client.get(reverse("core:index"))

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/")

    def test_any_page_anonymous_200(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 302)

    @responses.activate
    def test_logout_302(self):
        responses.add(
            responses.GET,
            f"{settings.NOTEBOOKS_HUB_URL}/logout",
            status=302,
        )

        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.post(reverse("logout"))

        # Check that the response is temporary redirection to JupyterHub logout.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")

    def test_graphql_anonymous(self):
        response = self.client.get(reverse("graphql"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("graphql") + "MyQuery/")
        self.assertEqual(response.status_code, 200)


class AcceptTosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "regular",
        )


class InviteUserAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "john@bluesquarehub.com",
            "passwd",
            is_superuser=True,
            is_staff=True,
        )
        cls.LEGACY_FEATURE = Feature.objects.create(code="openhexa_legacy")

    def test_invite_user(self):
        # an admin can invite a new user via django admin pages
        self.client.force_login(self.USER_ADMIN)
        self.assertEqual(User.objects.all().count(), 1)
        response = self.client.post(
            "/admin/user_management/user/add/",
            data={
                "email": "invited@bluesquarehub.com",
                "first_name": "daniel",
                "last_name": "mote",
                "password1": "",
                "password2": "",
                "membership_set-TOTAL_FORMS": 0,
                "membership_set-INITIAL_FORMS": 0,
                "featureflag_set-TOTAL_FORMS": 1,
                "featureflag_set-INITIAL_FORMS": 0,
                "featureflag_set-0-feature": self.LEGACY_FEATURE.id,
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.all().count(), 2)
