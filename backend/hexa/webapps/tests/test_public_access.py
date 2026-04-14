from unittest.mock import MagicMock, patch

import requests_mock
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner
from django.test import override_settings

from hexa.core.test import GraphQLTestCase, TestCase
from hexa.git.forgejo import ForgejoAPIError
from hexa.superset.models import SupersetInstance
from hexa.user_management.models import (
    Organization,
    User,
)
from hexa.webapps.models import GitWebapp, SupersetWebapp, Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class SupersetDashboardViewAccessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORG = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-public",
            organization_type="CORPORATE",
        )
        cls.SUPERSET_INSTANCE = SupersetInstance.objects.create(
            name="Superset",
            url="https://superset.example.com",
            api_username="test",
            api_password="password",
            organization=cls.ORG,
        )
        cls.USER_MEMBER = User.objects.create_user(
            "member@test.com",
            "password",
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "nonmember@test.com",
            "password",
        )
        cls.WORKSPACE = Workspace.objects.create(
            name="Test Workspace",
            organization=cls.ORG,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.WEBAPP_PRIVATE = SupersetWebapp.create_if_has_perm(
            principal=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            superset_instance=cls.SUPERSET_INSTANCE,
            external_dashboard_id="ext-private",
            name="Private Dashboard",
            created_by=cls.USER_MEMBER,
            is_public=False,
        )
        cls.DASHBOARD_PRIVATE = cls.WEBAPP_PRIVATE.superset_dashboard

        cls.WEBAPP_PUBLIC = SupersetWebapp.create_if_has_perm(
            principal=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            superset_instance=cls.SUPERSET_INSTANCE,
            external_dashboard_id="ext-public",
            name="Public Dashboard",
            created_by=cls.USER_MEMBER,
            is_public=True,
        )
        cls.DASHBOARD_PUBLIC = cls.WEBAPP_PUBLIC.superset_dashboard

    def _mock_superset(self, mocker):
        mocker.post(
            "https://superset.example.com/api/v1/security/login",
            json={"access_token": "token"},
        )
        mocker.get(
            "https://superset.example.com/api/v1/security/csrf_token/",
            headers={"Set-Cookie": "cookie"},
            json={"result": "csrf"},
        )
        mocker.post(
            "https://superset.example.com/api/v1/security/guest_token/",
            json={"token": "guest_token"},
        )

    def test_anonymous_cannot_view_private_superset_dashboard(self):
        url = f"/superset/dashboard/{self.DASHBOARD_PRIVATE.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_non_member_cannot_view_private_superset_dashboard(self):
        self.client.force_login(self.USER_NON_MEMBER)
        url = f"/superset/dashboard/{self.DASHBOARD_PRIVATE.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_member_can_view_private_superset_dashboard(self):
        self.client.force_login(self.USER_MEMBER)
        url = f"/superset/dashboard/{self.DASHBOARD_PRIVATE.id}/"
        with requests_mock.Mocker() as mocker:
            self._mock_superset(mocker)
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_can_view_public_superset_dashboard(self):
        url = f"/superset/dashboard/{self.DASHBOARD_PUBLIC.id}/"
        with requests_mock.Mocker() as mocker:
            self._mock_superset(mocker)
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_member_can_view_public_superset_dashboard(self):
        self.client.force_login(self.USER_NON_MEMBER)
        url = f"/superset/dashboard/{self.DASHBOARD_PUBLIC.id}/"
        with requests_mock.Mocker() as mocker:
            self._mock_superset(mocker)
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class IframeWebappAccessTest(GraphQLTestCase):
    WEBAPP_QUERY = """
        query Webapp($workspaceSlug: String!, $slug: String!) {
            webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                id
                name
            }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@iframe-test.com",
            "password",
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "nonmember@iframe-test.com",
            "password",
        )
        cls.WORKSPACE = Workspace.objects.create(name="Iframe Workspace")
        WorkspaceMembership.objects.create(
            user=cls.USER_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WEBAPP_PRIVATE = Webapp.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="Private Iframe",
            created_by=cls.USER_ADMIN,
            url="https://example.com",
            is_public=False,
        )
        cls.WEBAPP_PUBLIC = Webapp.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="Public Iframe",
            created_by=cls.USER_ADMIN,
            url="https://example.com",
            is_public=True,
        )

    def _query_webapp(self, webapp):
        return self.run_query(
            self.WEBAPP_QUERY,
            variables={
                "workspaceSlug": self.WORKSPACE.slug,
                "slug": webapp.slug,
            },
        )

    def test_anonymous_cannot_access_private_webapp(self):
        result = self._query_webapp(self.WEBAPP_PRIVATE)
        self.assertIsNone(result["data"]["webapp"])

    def test_anonymous_can_access_public_webapp(self):
        result = self._query_webapp(self.WEBAPP_PUBLIC)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Public Iframe")

    def test_non_member_cannot_access_private_webapp(self):
        self.client.force_login(self.USER_NON_MEMBER)
        result = self._query_webapp(self.WEBAPP_PRIVATE)
        self.assertIsNone(result["data"]["webapp"])

    def test_non_member_can_access_public_webapp(self):
        self.client.force_login(self.USER_NON_MEMBER)
        result = self._query_webapp(self.WEBAPP_PUBLIC)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Public Iframe")

    def test_member_can_access_private_webapp(self):
        self.client.force_login(self.USER_ADMIN)
        result = self._query_webapp(self.WEBAPP_PRIVATE)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Private Iframe")

    def test_member_can_access_public_webapp(self):
        self.client.force_login(self.USER_ADMIN)
        result = self._query_webapp(self.WEBAPP_PUBLIC)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Public Iframe")


class WebappURLValidationTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("xss@test.com", "password")
        cls.WORKSPACE = Workspace.objects.create(name="XSS Workspace")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def test_create_webapp_with_javascript_url_rejected(self):
        with self.assertRaises(ValidationError):
            Webapp.objects.create_if_has_perm(
                self.USER,
                self.WORKSPACE,
                name="XSS Webapp",
                created_by=self.USER,
                url="javascript:alert('XSS')",
            )

    def test_create_webapp_with_data_url_rejected(self):
        with self.assertRaises(ValidationError):
            Webapp.objects.create_if_has_perm(
                self.USER,
                self.WORKSPACE,
                name="Data Webapp",
                created_by=self.USER,
                url="data:text/html,<script>alert('XSS')</script>",
            )

    def test_create_webapp_with_https_url_accepted(self):
        webapp = Webapp.objects.create_if_has_perm(
            self.USER,
            self.WORKSPACE,
            name="HTTPS Webapp",
            created_by=self.USER,
            url="https://example.com",
        )
        self.assertEqual(webapp.url, "https://example.com")

    def test_update_webapp_with_javascript_url_rejected(self):
        webapp = Webapp.objects.create_if_has_perm(
            self.USER,
            self.WORKSPACE,
            name="Safe Webapp",
            created_by=self.USER,
            url="https://example.com",
        )
        self.client.force_login(self.USER)
        result = self.run_query(
            """
            mutation UpdateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                }
            }
            """,
            variables={
                "input": {
                    "id": str(webapp.id),
                    "source": {"iframe": {"url": "javascript:alert('XSS')"}},
                }
            },
        )
        self.assertFalse(result["data"]["updateWebapp"]["success"])
        self.assertIn("INVALID_URL", result["data"]["updateWebapp"]["errors"])
        webapp.refresh_from_db()
        self.assertEqual(webapp.url, "https://example.com")


@override_settings(
    WEBAPPS_DOMAIN="webapps.localhost:8000",
    ALLOWED_HOSTS=["*"],
)
class GitWebappServeViewTest(TestCase):
    SUBDOMAIN_BASE = "webapps.localhost:8000"

    @classmethod
    def setUpTestData(cls):
        cls.USER_MEMBER = User.objects.create_user(
            "servemember@test.com",
            "password",
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "servenonmember@test.com",
            "password",
        )
        cls.WORKSPACE = Workspace.objects.create(
            name="Serve Workspace",
            slug="serve-workspace",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.PRIVATE_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Private Git App",
            slug="private-git-app",
            subdomain="private-git-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER_MEMBER,
            repository="webapp-private",
            published_commit="sha-published",
            is_public=False,
        )

        cls.PUBLIC_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Public Git App",
            slug="public-git-app",
            subdomain="public-git-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER_MEMBER,
            repository="webapp-public",
            published_commit="sha-public",
            is_public=True,
        )

        cls.UNPUBLISHED_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Unpublished Git App",
            slug="unpublished-git-app",
            subdomain="unpublished-git-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER_MEMBER,
            repository="webapp-unpublished",
            is_public=True,
        )

    def _subdomain_host(self, webapp):
        return f"{webapp.subdomain}.{self.SUBDOMAIN_BASE}"

    def _get(self, webapp, path="/", **kwargs):
        return self.client.get(path, HTTP_HOST=self._subdomain_host(webapp), **kwargs)

    def _create_webapp_session(self, webapp, user):
        session = SessionStore()
        session.set_expiry(3600)
        session["user_id"] = str(user.pk)
        session["webapp_id"] = str(webapp.pk)
        session.create()
        self.client.cookies["hexa_webapp_session"] = session.session_key

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_serve_index_html(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<h1>Hello World</h1>"
        mock_get_client.return_value = mock_client

        self._create_webapp_session(self.PRIVATE_WEBAPP, self.USER_MEMBER)
        response = self._get(self.PRIVATE_WEBAPP)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"<h1>Hello World</h1>")
        self.assertEqual(response["Content-Type"], "text/html")

        mock_client.get_file.assert_called_once_with(
            "webapp-private",
            "index.html",
            "sha-published",
            org_slug="no-org",
        )

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_serve_css_file(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"body { color: red; }"
        mock_get_client.return_value = mock_client

        self._create_webapp_session(self.PRIVATE_WEBAPP, self.USER_MEMBER)
        response = self._get(self.PRIVATE_WEBAPP, "/style.css")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"body { color: red; }")
        self.assertEqual(response["Content-Type"], "text/css")

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_serve_js_file(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"console.log('hello');"
        mock_get_client.return_value = mock_client

        self._create_webapp_session(self.PRIVATE_WEBAPP, self.USER_MEMBER)
        response = self._get(self.PRIVATE_WEBAPP, "/script.js")

        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response["Content-Type"])

    def test_serve_nonexistent_webapp(self):
        response = self.client.get("/", HTTP_HOST=f"nonexistent.{self.SUBDOMAIN_BASE}")
        self.assertEqual(response.status_code, 404)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_serve_unpublished_webapp(self, mock_get_client):
        response = self._get(self.UNPUBLISHED_WEBAPP)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_redirected_to_auth_for_private_webapp(self):
        response = self._get(self.PRIVATE_WEBAPP)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth-token/", response["Location"])

    def test_non_member_redirected_to_auth_for_private_webapp(self):
        response = self._get(self.PRIVATE_WEBAPP)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth-token/", response["Location"])

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_member_can_access_private_webapp(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html>private</html>"
        mock_get_client.return_value = mock_client

        self._create_webapp_session(self.PRIVATE_WEBAPP, self.USER_MEMBER)
        response = self._get(self.PRIVATE_WEBAPP)
        self.assertEqual(response.status_code, 200)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_anonymous_can_access_public_webapp(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html>public</html>"
        mock_get_client.return_value = mock_client

        response = self._get(self.PUBLIC_WEBAPP)
        self.assertEqual(response.status_code, 200)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_non_member_can_access_public_webapp(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html>public</html>"
        mock_get_client.return_value = mock_client

        response = self._get(self.PUBLIC_WEBAPP)
        self.assertEqual(response.status_code, 200)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_serve_file_not_found_in_forgejo(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.side_effect = ForgejoAPIError(
            "GET", "http://forgejo/api", 404, "not found"
        )
        mock_get_client.return_value = mock_client

        self._create_webapp_session(self.PRIVATE_WEBAPP, self.USER_MEMBER)
        response = self._get(self.PRIVATE_WEBAPP, "/nonexistent.html")
        self.assertEqual(response.status_code, 404)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_serve_nested_path(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b".icon { display: block; }"
        mock_get_client.return_value = mock_client

        self._create_webapp_session(self.PRIVATE_WEBAPP, self.USER_MEMBER)
        response = self._get(self.PRIVATE_WEBAPP, "/assets/icons/style.css")

        self.assertEqual(response.status_code, 200)
        mock_client.get_file.assert_called_once_with(
            "webapp-private",
            "assets/icons/style.css",
            "sha-published",
            org_slug="no-org",
        )

    def test_invalid_session_cookie_redirects_to_auth(self):
        self.client.cookies["hexa_webapp_session"] = "nonexistent-session-key"
        response = self._get(self.PRIVATE_WEBAPP)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth-token/", response["Location"])

    def test_session_for_wrong_webapp_redirects_to_auth(self):
        session = SessionStore()
        session.set_expiry(3600)
        session["user_id"] = str(self.USER_MEMBER.pk)
        session["webapp_id"] = str(self.PUBLIC_WEBAPP.pk)
        session.create()

        self.client.cookies["hexa_webapp_session"] = session.session_key
        response = self._get(self.PRIVATE_WEBAPP)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth-token/", response["Location"])

    def test_graphql_blocked_on_subdomain(self):
        response = self.client.get(
            "/graphql/", HTTP_HOST=self._subdomain_host(self.PUBLIC_WEBAPP)
        )
        self.assertEqual(response.status_code, 404)


@override_settings(
    WEBAPPS_DOMAIN="webapps.localhost:8000",
    ALLOWED_HOSTS=["*"],
    BASE_URL="http://localhost:8000",
)
class AuthTokenViewTest(TestCase):
    SUBDOMAIN_BASE = "webapps.localhost:8000"

    @classmethod
    def setUpTestData(cls):
        cls.USER_MEMBER = User.objects.create_user(
            "authmember@test.com",
            "password",
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "authnonmember@test.com",
            "password",
        )
        cls.WORKSPACE = Workspace.objects.create(
            name="Auth Workspace",
            slug="auth-workspace",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.PRIVATE_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Auth Private App",
            slug="auth-private-app",
            subdomain="auth-private-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER_MEMBER,
            repository="webapp-auth",
            published_commit="sha-auth",
            is_public=False,
        )
        cls.PUBLIC_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Auth Public App",
            slug="auth-public-app",
            subdomain="auth-public-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER_MEMBER,
            repository="webapp-auth-pub",
            published_commit="sha-pub",
            is_public=True,
        )

    def _auth_token_url(self, webapp):
        return f"/webapps/{webapp.pk}/auth-token/"

    def _webapp_url(self, webapp, path="/"):
        return f"http://{webapp.subdomain}.{self.SUBDOMAIN_BASE}{path}"

    def test_member_gets_token_redirect(self):
        self.client.force_login(self.USER_MEMBER)
        next_url = self._webapp_url(self.PRIVATE_WEBAPP)
        response = self.client.get(
            self._auth_token_url(self.PRIVATE_WEBAPP), {"next": next_url}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("auth_token=", response["Location"])
        self.assertTrue(response["Location"].startswith(next_url))

    def test_non_member_forbidden(self):
        self.client.force_login(self.USER_NON_MEMBER)
        next_url = self._webapp_url(self.PRIVATE_WEBAPP)
        response = self.client.get(
            self._auth_token_url(self.PRIVATE_WEBAPP), {"next": next_url}
        )
        self.assertEqual(response.status_code, 403)

    def test_public_webapp_grants_token_to_anyone(self):
        self.client.force_login(self.USER_NON_MEMBER)
        next_url = self._webapp_url(self.PUBLIC_WEBAPP)
        response = self.client.get(
            self._auth_token_url(self.PUBLIC_WEBAPP), {"next": next_url}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("auth_token=", response["Location"])

    def test_missing_next_parameter(self):
        self.client.force_login(self.USER_MEMBER)
        response = self.client.get(self._auth_token_url(self.PRIVATE_WEBAPP))
        self.assertEqual(response.status_code, 400)

    def test_mismatched_subdomain_rejected(self):
        self.client.force_login(self.USER_MEMBER)
        wrong_url = f"http://evil.{self.SUBDOMAIN_BASE}/"
        response = self.client.get(
            self._auth_token_url(self.PRIVATE_WEBAPP), {"next": wrong_url}
        )
        self.assertEqual(response.status_code, 400)


@override_settings(
    WEBAPPS_DOMAIN="webapps.localhost:8000",
    ALLOWED_HOSTS=["*"],
    BASE_URL="http://localhost:8000",
)
class MiddlewareAuthTokenExchangeTest(TestCase):
    SUBDOMAIN_BASE = "webapps.localhost:8000"

    @classmethod
    def setUpTestData(cls):
        cls.USER_MEMBER = User.objects.create_user(
            "mwmember@test.com",
            "password",
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "mwnonmember@test.com",
            "password",
        )
        cls.WORKSPACE = Workspace.objects.create(
            name="MW Workspace",
            slug="mw-workspace",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.PRIVATE_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="MW Private App",
            slug="mw-private-app",
            subdomain="mw-private-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER_MEMBER,
            repository="webapp-mw",
            published_commit="sha-mw",
            is_public=False,
        )
        cls.OTHER_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="MW Other App",
            slug="mw-other-app",
            subdomain="mw-other-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER_MEMBER,
            repository="webapp-mw-other",
            published_commit="sha-other",
            is_public=False,
        )

    def _subdomain_host(self, webapp):
        return f"{webapp.subdomain}.{self.SUBDOMAIN_BASE}"

    def _sign_token(self, user, subdomain):
        signer = TimestampSigner()
        return signer.sign_object({"user_id": str(user.id), "subdomain": subdomain})

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_valid_token_creates_session_and_redirects(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html>ok</html>"
        mock_get_client.return_value = mock_client

        token = self._sign_token(self.USER_MEMBER, self.PRIVATE_WEBAPP.subdomain)

        host = self._subdomain_host(self.PRIVATE_WEBAPP)
        response = self.client.get(
            "/",
            {"auth_token": token},
            HTTP_HOST=host,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertIn("hexa_webapp_session", response.cookies)

        session_key = response.cookies["hexa_webapp_session"].value
        session = SessionStore(session_key=session_key)
        self.assertEqual(session["user_id"], str(self.USER_MEMBER.pk))
        self.assertEqual(session["webapp_id"], str(self.PRIVATE_WEBAPP.pk))

        response = self.client.get("/", HTTP_HOST=host)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"<html>ok</html>")

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_full_auth_flow_token_then_session(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html>private</html>"
        mock_get_client.return_value = mock_client

        token = self._sign_token(self.USER_MEMBER, self.PRIVATE_WEBAPP.subdomain)
        host = self._subdomain_host(self.PRIVATE_WEBAPP)

        response = self.client.get("/", {"auth_token": token}, HTTP_HOST=host)
        self.assertEqual(response.status_code, 302)
        self.assertIn("hexa_webapp_session", response.cookies)

        response = self.client.get("/", HTTP_HOST=host)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"<html>private</html>")

    def test_tampered_token_redirects_to_auth(self):
        response = self.client.get(
            "/",
            {"auth_token": "bad-token"},
            HTTP_HOST=self._subdomain_host(self.PRIVATE_WEBAPP),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth-token/", response["Location"])

    def test_token_for_wrong_subdomain_forbidden(self):
        token = self._sign_token(self.USER_MEMBER, self.OTHER_WEBAPP.subdomain)
        response = self.client.get(
            "/",
            {"auth_token": token},
            HTTP_HOST=self._subdomain_host(self.PRIVATE_WEBAPP),
        )
        self.assertEqual(response.status_code, 403)

    def test_token_for_non_member_forbidden(self):
        token = self._sign_token(self.USER_NON_MEMBER, self.PRIVATE_WEBAPP.subdomain)
        response = self.client.get(
            "/",
            {"auth_token": token},
            HTTP_HOST=self._subdomain_host(self.PRIVATE_WEBAPP),
        )
        self.assertEqual(response.status_code, 403)

    def test_token_preserves_query_params(self):
        token = self._sign_token(self.USER_MEMBER, self.PRIVATE_WEBAPP.subdomain)
        response = self.client.get(
            "/page",
            {"auth_token": token, "foo": "bar"},
            HTTP_HOST=self._subdomain_host(self.PRIVATE_WEBAPP),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/page?foo=bar")


@override_settings(
    WEBAPPS_DOMAIN="webapps.localhost:8000",
    ALLOWED_HOSTS=["*"],
)
class PoweredByBannerTest(TestCase):
    SUBDOMAIN_BASE = "webapps.localhost:8000"

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("banner@test.com", "password")
        cls.WORKSPACE = Workspace.objects.create(
            name="Banner Workspace",
            slug="banner-workspace",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.PUBLIC_STATIC = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Public Static",
            slug="public-static",
            subdomain="public-static",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-pub-static",
            published_commit="sha-pub",
            is_public=True,
            show_powered_by=True,
        )

        cls.PUBLIC_STATIC_NO_BANNER = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Public Static No Banner",
            slug="public-static-no-banner",
            subdomain="pub-static-no-banner",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-pub-no-banner",
            published_commit="sha-pub-nb",
            is_public=True,
            show_powered_by=False,
        )

        cls.PRIVATE_STATIC = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Private Static",
            slug="private-static",
            subdomain="private-static",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-priv-static",
            published_commit="sha-priv",
            is_public=False,
        )

        cls.PUBLIC_IFRAME = Webapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Public Iframe",
            slug="public-iframe-banner",
            subdomain="public-iframe-banner",
            type=Webapp.WebappType.IFRAME,
            created_by=cls.USER,
            url="https://example.com",
            is_public=True,
            show_powered_by=True,
        )

        cls.PUBLIC_IFRAME_NO_BANNER = Webapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Public Iframe No Banner",
            slug="pub-iframe-no-banner",
            subdomain="pub-iframe-no-banner",
            type=Webapp.WebappType.IFRAME,
            created_by=cls.USER,
            url="https://example.com",
            is_public=True,
            show_powered_by=False,
        )

    def _subdomain_host(self, webapp):
        return f"{webapp.subdomain}.{self.SUBDOMAIN_BASE}"

    def _create_webapp_session(self, webapp, user):
        session = SessionStore()
        session.set_expiry(3600)
        session["user_id"] = str(user.pk)
        session["webapp_id"] = str(webapp.pk)
        session.create()
        self.client.cookies["hexa_webapp_session"] = session.session_key

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_static_public_anonymous_has_banner(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html><body><h1>Hi</h1></body></html>"
        mock_get_client.return_value = mock_client

        response = self.client.get(
            "/", HTTP_HOST=self._subdomain_host(self.PUBLIC_STATIC)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Powered by", response.content)
        self.assertIn(b"openhexa.com", response.content)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_static_public_anonymous_show_powered_by_false_no_banner(
        self, mock_get_client
    ):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html><body><h1>Hi</h1></body></html>"
        mock_get_client.return_value = mock_client

        response = self.client.get(
            "/", HTTP_HOST=self._subdomain_host(self.PUBLIC_STATIC_NO_BANNER)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Powered by", response.content)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_static_private_authenticated_no_banner(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html><body><h1>Hi</h1></body></html>"
        mock_get_client.return_value = mock_client

        self._create_webapp_session(self.PRIVATE_STATIC, self.USER)
        response = self.client.get(
            "/", HTTP_HOST=self._subdomain_host(self.PRIVATE_STATIC)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Powered by", response.content)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_static_banner_not_injected_in_css(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"body { color: red; }"
        mock_get_client.return_value = mock_client

        response = self.client.get(
            "/style.css", HTTP_HOST=self._subdomain_host(self.PUBLIC_STATIC)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Powered by", response.content)

    def test_iframe_public_anonymous_has_banner(self):
        response = self.client.get(
            "/", HTTP_HOST=self._subdomain_host(self.PUBLIC_IFRAME)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Powered by", response.content)
        self.assertIn(b"oh-banner", response.content)

    def test_iframe_public_anonymous_show_powered_by_false_no_banner(self):
        response = self.client.get(
            "/", HTTP_HOST=self._subdomain_host(self.PUBLIC_IFRAME_NO_BANNER)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Powered by", response.content)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_static_public_with_auth_token_no_banner(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html><body><h1>Hi</h1></body></html>"
        mock_get_client.return_value = mock_client

        signer = TimestampSigner()
        token = signer.sign_object(
            {"user_id": str(self.USER.id), "subdomain": self.PUBLIC_STATIC.subdomain}
        )
        response = self.client.get(
            "/",
            {"auth_token": token},
            HTTP_HOST=self._subdomain_host(self.PUBLIC_STATIC),
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Powered by", response.content)


@override_settings(
    WEBAPPS_DOMAIN="webapps.localhost",
    BASE_HOSTNAME="localhost",
    ALLOWED_HOSTS=["*"],
    BASE_URL="http://localhost:8000",
)
class CustomDomainMiddlewareTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("cdm@test.com", "password")
        cls.WORKSPACE = Workspace.objects.create(name="CDM Workspace")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.PUBLIC_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Custom Domain App",
            slug="custom-domain-app",
            subdomain="custom-domain-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-custom",
            published_commit="sha-custom",
            is_public=True,
            custom_domain="mycustomdomain.com",
        )
        cls.PRIVATE_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Private Custom Domain App",
            slug="private-custom-domain-app",
            subdomain="private-custom-domain-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-private-custom",
            published_commit="sha-private-custom",
            is_public=False,
            custom_domain="privatecustomdomain.com",
        )

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_public_webapp_served_on_custom_domain(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html>custom</html>"
        mock_get_client.return_value = mock_client

        response = self.client.get("/", HTTP_HOST="mycustomdomain.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"<html>custom</html>")

    def test_private_webapp_not_served_on_custom_domain(self):
        response = self.client.get("/", HTTP_HOST="privatecustomdomain.com")
        self.assertNotEqual(response.status_code, 200)

    def test_unknown_custom_domain_passes_through(self):
        response = self.client.get("/", HTTP_HOST="unknowndomain.com")
        self.assertNotEqual(response.status_code, 200)

    def test_graphql_blocked_on_custom_domain(self):
        response = self.client.get("/graphql/", HTTP_HOST="mycustomdomain.com")
        self.assertEqual(response.status_code, 404)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_csp_header_set_on_custom_domain(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html>custom</html>"
        mock_get_client.return_value = mock_client

        response = self.client.get("/", HTTP_HOST="mycustomdomain.com")
        self.assertIn("frame-ancestors", response.get("Content-Security-Policy", ""))

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_main_hostname_not_intercepted(self, mock_get_client):
        self.client.get("/", HTTP_HOST="localhost")
        mock_get_client.assert_not_called()

    @patch("hexa.webapps.middlewares.Webapp.objects.get")
    def test_webapp_subdomain_not_intercepted(self, mock_get):
        self.client.get("/", HTTP_HOST="custom-domain-app.webapps.localhost")
        for call in mock_get.call_args_list:
            self.assertNotIn("custom_domain", call.kwargs)
