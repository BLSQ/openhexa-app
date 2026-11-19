import time
from unittest.mock import patch

import responses
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import Organization, User
from hexa.user_management.utils import LOGIN_LINK_MAX_AGE, get_login_url


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


class LoginLinkViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(name="Org")
        cls.OWNER = User.objects.create_user("owner@example.org", "password")

    def test_logs_in_and_opens_organization(self):
        response = self.client.get(get_login_url(self.OWNER, self.ORGANIZATION))

        self.assertRedirects(
            response,
            f"{settings.NEW_FRONTEND_DOMAIN}/organizations/{self.ORGANIZATION.id}",
            fetch_redirect_response=False,
        )
        self.assertEqual(self.client.session[SESSION_KEY], str(self.OWNER.id))

    def _assert_redirects_to_login_then_organization(self, response):
        self.assertRedirects(
            response,
            f"{settings.NEW_FRONTEND_DOMAIN}/login?next=%2Forganizations%2F{self.ORGANIZATION.id}",
            fetch_redirect_response=False,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_used_link_leads_to_login_then_organization(self):
        url = get_login_url(self.OWNER, self.ORGANIZATION)
        self.client.get(url)
        self.client.logout()

        self._assert_redirects_to_login_then_organization(self.client.get(url))

    def test_used_link_opens_organization_for_its_logged_in_owner(self):
        url = get_login_url(self.OWNER, self.ORGANIZATION)
        self.client.get(url)

        response = self.client.get(url)

        self.assertRedirects(
            response,
            f"{settings.NEW_FRONTEND_DOMAIN}/organizations/{self.ORGANIZATION.id}",
            fetch_redirect_response=False,
        )

    def test_used_link_does_not_open_organization_for_another_user(self):
        url = get_login_url(self.OWNER, self.ORGANIZATION)
        self.client.get(url)
        self.client.logout()
        self.client.force_login(User.objects.create_user("other@example.org", "pw"))

        response = self.client.get(url)

        self.assertRedirects(
            response,
            f"{settings.NEW_FRONTEND_DOMAIN}/login?next=%2Forganizations%2F{self.ORGANIZATION.id}",
            fetch_redirect_response=False,
        )

    def test_expired_link_leads_to_login_then_organization(self):
        issued_at = time.time() - LOGIN_LINK_MAX_AGE.total_seconds() - 1
        with patch("django.core.signing.time.time", return_value=issued_at):
            url = get_login_url(self.OWNER, self.ORGANIZATION)

        self._assert_redirects_to_login_then_organization(self.client.get(url))

    def test_tampered_link_leads_to_login(self):
        url = get_login_url(self.OWNER, self.ORGANIZATION)

        with self.assertLogs("hexa.user_management.views", level="WARNING"):
            response = self.client.get(url.rstrip("/") + "x/")

        self.assertRedirects(
            response,
            f"{settings.NEW_FRONTEND_DOMAIN}/login",
            fetch_redirect_response=False,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)
