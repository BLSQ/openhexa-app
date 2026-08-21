import gzip
from unittest.mock import patch

from django.test import override_settings

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp
from hexa.webapps.tests.testutils import (
    make_gzipped_upstream,
    make_upstream,
    read_body,
)
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

    def _get(self, path="/", **kwargs):
        return self.client.get(
            path, HTTP_HOST=f"{self.WEBAPP.subdomain}.{self.SUBDOMAIN_BASE}", **kwargs
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

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_precompressed_asset_is_not_gzipped(self, mock_get_client):
        payload = b"PMTiles" + b"\x00\x01\x02\x03" * 200
        mock_get_client.return_value.stream_file.return_value = make_upstream(payload)

        response = self._get("/buildings.pmtiles", HTTP_ACCEPT_ENCODING="gzip")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Content-Encoding", response)
        self.assertEqual(read_body(response), payload)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_image_asset_is_not_gzipped(self, mock_get_client):
        mock_get_client.return_value.stream_file.return_value = make_upstream(
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 500
        )

        response = self._get("/logo.png", HTTP_ACCEPT_ENCODING="gzip")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Content-Encoding", response)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_svg_is_still_gzipped(self, mock_get_client):
        # SVG is the image/* type that is plain text and compresses well.
        svg = b'<svg xmlns="http://www.w3.org/2000/svg">' + b"<rect/>" * 100 + b"</svg>"
        mock_get_client.return_value.stream_file.return_value = make_upstream(svg)

        response = self._get("/icon.svg", HTTP_ACCEPT_ENCODING="gzip")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Encoding"], "gzip")
        self.assertEqual(gzip.decompress(read_body(response)), svg)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_gzipped_upstream_body_is_relayed_untouched(self, mock_get_client):
        """A content-encoded upstream body must reach the client as it arrived."""
        payload = b'{"features":' + b'"x"' * 2000 + b"}"
        upstream = make_gzipped_upstream(payload)
        mock_get_client.return_value.stream_file.return_value = upstream

        response = self._get("/data.json", HTTP_ACCEPT_ENCODING="gzip")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Encoding"], "gzip")
        body = read_body(response)
        self.assertEqual(body, gzip.compress(payload, mtime=0))
        self.assertEqual(response["Content-Length"], str(len(body)))
        self.assertEqual(gzip.decompress(body), payload)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_gzipped_upstream_is_not_gzipped_again(self, mock_get_client):
        payload = b"col_a,col_b\n" + b"1,2\n" * 200
        mock_get_client.return_value.stream_file.return_value = make_gzipped_upstream(
            payload
        )

        response = self._get("/data.csv", HTTP_ACCEPT_ENCODING="gzip")

        self.assertEqual(response["Content-Encoding"], "gzip")
        self.assertEqual(gzip.decompress(read_body(response)), payload)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_upstream_is_asked_not_to_compress(self, mock_get_client):
        mock_get_client.return_value.stream_file.return_value = make_upstream(b"data")

        self._get("/buildings.pmtiles")

        _, kwargs = mock_get_client.return_value.stream_file.call_args
        self.assertNotIn("Accept-Encoding", kwargs["headers"])

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_partial_response_is_not_gzipped(self, mock_get_client):
        body = b"y" * 400
        mock_get_client.return_value.stream_file.return_value = make_upstream(
            body,
            status=206,
            headers={"Content-Range": f"bytes 0-399/{400 * 10}"},
        )

        response = self._get(
            "/data.json", HTTP_RANGE="bytes=0-399", HTTP_ACCEPT_ENCODING="gzip"
        )

        self.assertEqual(response.status_code, 206)
        self.assertNotIn("Content-Encoding", response)
        self.assertEqual(read_body(response), body)
