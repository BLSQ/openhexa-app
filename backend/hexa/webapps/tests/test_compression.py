import gzip
from unittest.mock import patch

from django.test import override_settings

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp
from hexa.workspaces.tests.testutils import create_workspace


@override_settings(
    WEBAPPS_DOMAIN="webapps.localhost:8000",
    ALLOWED_HOSTS=["*"],
)
class WebappCompressionTest(TestCase):
    """Nothing downstream of Django compresses in production (GCLB does no
    dynamic compression), so GZipMiddleware must gzip webapp responses itself —
    and it must run *after* the middlewares that rewrite the response body
    (banner/context injection), otherwise those would corrupt the gzip stream.
    """

    SUBDOMAIN_BASE = "webapps.localhost:8000"
    # GZipMiddleware skips bodies under 200 bytes; make ours comfortably bigger.
    HTML = b"<html><head></head><body>" + b"x" * 500 + b"</body></html>"

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("gzip@test.com", "password")
        cls.WORKSPACE = create_workspace(name="Gzip Workspace", slug="gzip-workspace")
        cls.WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Gzip Public",
            slug="gzip-public",
            subdomain="gzip-public",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="gzip-public-repo",
            published_commit="sha-gzip-v1",
            is_public=True,
        )

    def _get(self, **kwargs):
        return self.client.get(
            "/", HTTP_HOST=f"{self.WEBAPP.subdomain}.{self.SUBDOMAIN_BASE}", **kwargs
        )

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_response_is_gzipped_when_client_accepts_it(self, mock_get_client):
        mock_get_client.return_value.get_file.return_value = self.HTML

        response = self._get(HTTP_ACCEPT_ENCODING="gzip")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Encoding"], "gzip")
        self.assertIn("Accept-Encoding", response["Vary"])
        # The ETag must stay weak so the 304 revalidation flow keeps working
        # on compressed representations.
        self.assertEqual(response["ETag"], 'W/"sha-gzip-v1"')

        body = gzip.decompress(response.content)
        # Body injection (banner, OPENHEXA context) must have happened before
        # compression — the decompressed payload is the fully rewritten HTML.
        self.assertIn(b"x" * 500, body)
        self.assertIn(b"window.OPENHEXA", body)
        self.assertIn(b"Powered by", body)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_response_is_not_gzipped_without_accept_encoding(self, mock_get_client):
        mock_get_client.return_value.get_file.return_value = self.HTML

        response = self._get(HTTP_ACCEPT_ENCODING="identity")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Content-Encoding", response)
        self.assertIn(b"x" * 500, response.content)
