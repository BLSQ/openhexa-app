import responses
from django.conf import settings
from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import User


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

    @responses.activate
    def test_logout_forwards_the_configured_cookie_names(self):
        responses.add(responses.GET, f"{settings.NOTEBOOKS_HUB_URL}/logout", status=302)

        with self.settings(
            SESSION_COOKIE_NAME="sessionid_demo", CSRF_COOKIE_NAME="csrftoken_demo"
        ):
            self.client.force_login(self.USER_REGULAR)
            session_key = self.client.cookies["sessionid_demo"].value
            self.client.post(reverse("logout"))

        cookie_header = responses.calls[0].request.headers["Cookie"]
        self.assertIn(f"sessionid_demo={session_key}", cookie_header)
        self.assertIn("csrftoken_demo=", cookie_header)

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
