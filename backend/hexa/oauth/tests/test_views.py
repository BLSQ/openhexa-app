from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken

from hexa.oauth.views import OAuthAuthorizeView, gitea_authorize
from hexa.user_management.models import User

GITEA_CLIENT_ID = "e90ee53c-94e2-48ac-9358-a874fb9e0662"


class GitOAuthClientTest(TestCase):
    def test_gitea_and_generic_clients_exist(self):
        """The hexa.git migration registers both git OAuth clients as public apps."""
        for client_id in (GITEA_CLIENT_ID, "openhexa-git"):
            app = Application.objects.get(client_id=client_id)
            self.assertEqual(app.client_type, "public")
            self.assertEqual(app.authorization_grant_type, "authorization-code")
            self.assertIn("http://127.0.0.1/", app.redirect_uris)


class GiteaAuthorizeScopeTest(TestCase):
    def test_pins_git_scope_when_none_requested(self):
        """GCM's Gitea flow sends no scope; we must redirect with openhexa:git pinned."""
        request = RequestFactory().get(
            "/login/oauth/authorize",
            {"client_id": GITEA_CLIENT_ID, "response_type": "code"},
        )
        request.user = AnonymousUser()
        response = gitea_authorize(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("scope=openhexa%3Agit", response["Location"])


class GiteaOAuthRoutingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("dev@bluesquarehub.com", "password")

    def test_authorize_route_requires_login(self):
        """Unauthenticated authorize must bounce to the OpenHEXA sign-in."""
        response = self.client.get(
            "/login/oauth/authorize",
            {"client_id": GITEA_CLIENT_ID, "response_type": "code"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response["Location"])

    def test_authorize_pins_scope_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(
            "/login/oauth/authorize",
            {
                "client_id": GITEA_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": "http://127.0.0.1/",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("scope=openhexa%3Agit", response["Location"])

    def test_token_endpoint_is_anonymous(self):
        """The token POST carries no session; it must reach DOT, not the login wall.

        A login redirect would be 302; DOT rejecting an empty grant is 400, which
        proves the request got through the anonymous-URL whitelist.
        """
        response = self.client.post("/login/oauth/access_token", {})
        self.assertEqual(response.status_code, 400)


class GitTokenRefreshTest(TestCase):
    """Exercises the refresh_token grant the way Git Credential Manager does."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("refresh@bluesquarehub.com", "pw")
        cls.app = Application.objects.get(client_id=GITEA_CLIENT_ID)

    def _seed_refresh_token(self):
        access = AccessToken.objects.create(
            user=self.user,
            application=self.app,
            token="seed-access-token",
            expires=timezone.now() + timedelta(hours=1),
            scope="openhexa:git",
        )
        RefreshToken.objects.create(
            user=self.user,
            application=self.app,
            token="seed-refresh-token",
            access_token=access,
        )

    def test_refresh_grant_issues_new_long_lived_token(self):
        """Refresh works silently (no browser) and the git token is long-lived.

        The long ``expires_in`` is what stops Git Credential Manager from letting
        the token expire between sessions, avoiding the first-request-fails hiccup.
        """
        self._seed_refresh_token()
        response = self.client.post(
            "/login/oauth/access_token",
            {
                "grant_type": "refresh_token",
                "refresh_token": "seed-refresh-token",
                "client_id": GITEA_CLIENT_ID,
                "scope": "openhexa:git",
            },
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data.get("scope"), "openhexa:git")
        # Git tokens get the long lifetime even when minted via refresh.
        self.assertGreater(data["expires_in"], 24 * 60 * 60)


class OAuthAuthorizeRedirectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.application = Application.objects.get(client_id="openhexa-git")

    def test_redirect_renders_success_page(self):
        view = OAuthAuthorizeView()
        for target in (
            "http://127.0.0.1:54321/?code=abc",
            "https://claude.ai/callback?code=abc",
        ):
            response = view.redirect(target, self.application)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"redirectUri", response.content)
            self.assertIn(b"Authorization successful", response.content)
