import json
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace


class MainHostFromWebappOriginTest(TestCase):
    """Web app pages must go through the proxy: their origin must not be able
    to call the main host with the user's session.

    The web app origin is built from the WEBAPPS_DOMAIN the settings were
    loaded with (set by docker-compose for tests and CI), so these tests
    exercise the CORS rules production actually computes from it.
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("origin@test.com", "password")
        cls.WORKSPACE = create_workspace(name="Origin WS")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def setUp(self):
        super().setUp()
        self.assertIsNotNone(
            settings.WEBAPPS_DOMAIN_HOST,
            "WEBAPPS_DOMAIN must be set in the environment for these tests",
        )
        self.webapp_origin = f"https://probe-app.{settings.WEBAPPS_DOMAIN_HOST}"
        self.client.force_login(self.USER)

    def _preflight(self, path, origin):
        return self.client.options(
            path,
            HTTP_ORIGIN=origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

    def test_graphql_preflight_from_webapp_origin_is_refused(self):
        response = self._preflight("/graphql/", self.webapp_origin)
        self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_graphql_post_from_webapp_origin_is_not_readable(self):
        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": "query { me { user { email } } }"}),
            content_type="application/json",
            HTTP_ORIGIN=self.webapp_origin,
        )
        self.assertNotIn("Access-Control-Allow-Origin", response)
        self.assertNotIn("Access-Control-Allow-Credentials", response)

    def test_credentialed_paths_refuse_webapp_origin(self):
        for path in [
            "/mcp/",
            "/oauth/token/",
            "/analytics/track/",
            "/pipelines/runs/some-run/messages/stream/",
            "/assistant/conversations/some-conversation/stream/",
        ]:
            with self.subTest(path=path):
                response = self._preflight(path, self.webapp_origin)
                self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_file_transfer_paths_allow_webapp_origin(self):
        # Download/upload URLs handed out by prepareObjectDownload/Upload point
        # at the main host on the filesystem backend. Their views authenticate
        # with the token in the URL and never read the session, so the
        # Access-Control-Allow-Credentials header (global in django-cors-headers)
        # grants nothing there.
        for path in ["/files/dl/sometoken/", "/files/up/sometoken/"]:
            with self.subTest(path=path):
                response = self._preflight(path, self.webapp_origin)
                self.assertEqual(
                    response.get("Access-Control-Allow-Origin"), self.webapp_origin
                )

    @patch("hexa.webapps.middlewares.sentry_sdk")
    def test_refused_request_is_reported_to_sentry(self, mock_sentry):
        response = self._preflight("/graphql/", self.webapp_origin)
        self.assertEqual(response.status_code, 403)
        mock_sentry.capture_message.assert_called_once_with(
            "Refused a webapp request to the main host", level="warning"
        )

    def test_webapp_origin_cannot_mutate_via_simple_request(self):
        # multipart/form-data is a CORS "simple" request: the browser sends it
        # without a preflight, so CORS alone cannot stop it.
        original_name = self.WORKSPACE.name
        self.client.post(
            "/graphql/",
            data={
                "operations": json.dumps(
                    {
                        "query": f"""
                        mutation {{
                            updateWorkspace(input: {{slug: "{self.WORKSPACE.slug}", name: "PWNED"}}) {{
                                success
                            }}
                        }}
                        """
                    }
                ),
                "map": "{}",
            },
            HTTP_ORIGIN=self.webapp_origin,
        )
        self.WORKSPACE.refresh_from_db()
        self.assertEqual(self.WORKSPACE.name, original_name)

    def test_frontend_origin_keeps_cors_on_graphql(self):
        response = self._preflight("/graphql/", settings.NEW_FRONTEND_DOMAIN)
        self.assertEqual(
            response.get("Access-Control-Allow-Origin"), settings.NEW_FRONTEND_DOMAIN
        )
