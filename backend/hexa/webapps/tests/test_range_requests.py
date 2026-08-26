from unittest.mock import MagicMock, patch

from django.test import override_settings

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp
from hexa.webapps.tests.testutils import make_upstream, read_body
from hexa.workspaces.tests.testutils import create_workspace

TOTAL_SIZE = 108570598


@override_settings(
    WEBAPPS_DOMAIN="webapps.localhost:8000",
    ALLOWED_HOSTS=["*"],
)
class WebappRangeRequestTest(TestCase):
    SUBDOMAIN_BASE = "webapps.localhost:8000"

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("range@test.com", "password")
        cls.WORKSPACE = create_workspace(name="Range Workspace", slug="range-workspace")
        cls.WEBAPP = GitWebapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Range Public",
            slug="range-public",
            subdomain="range-public",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="range-public-repo",
            published_commit="sha-range-v1",
            is_public=True,
        )

    def _get(self, path, **kwargs):
        return self.client.get(
            path, HTTP_HOST=f"{self.WEBAPP.subdomain}.{self.SUBDOMAIN_BASE}", **kwargs
        )

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_range_request_returns_partial_content(self, mock_get_client):
        chunk = b"PMTiles" + b"\x00" * 16377
        mock_client = MagicMock()
        mock_client.stream_file.return_value = make_upstream(
            chunk,
            status=206,
            headers={"Content-Range": f"bytes 0-16383/{TOTAL_SIZE}"},
        )
        mock_get_client.return_value = mock_client

        response = self._get("/buildings.pmtiles", HTTP_RANGE="bytes=0-16383")

        self.assertEqual(response.status_code, 206)
        self.assertEqual(response["Content-Range"], f"bytes 0-16383/{TOTAL_SIZE}")
        self.assertEqual(response["Content-Length"], str(len(chunk)))
        self.assertEqual(response["Accept-Ranges"], "bytes")
        self.assertEqual(read_body(response), chunk)

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_range_header_is_forwarded_upstream(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.stream_file.return_value = make_upstream(b"partial", status=206)
        mock_get_client.return_value = mock_client

        self._get("/buildings.pmtiles", HTTP_RANGE="bytes=1000-2000")

        mock_client.stream_file.assert_called_once_with(
            "range-public-repo",
            "buildings.pmtiles",
            "sha-range-v1",
            org_slug=self.WORKSPACE.organization.slug,
            headers={"Range": "bytes=1000-2000"},
        )

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_full_request_advertises_range_support(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.stream_file.return_value = make_upstream(b"whole file")
        mock_get_client.return_value = mock_client

        response = self._get("/buildings.pmtiles")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Accept-Ranges"], "bytes")
        self.assertEqual(mock_client.stream_file.call_args.kwargs["headers"], {})

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_only_whitelisted_request_headers_reach_the_git_backend(
        self, mock_get_client
    ):
        mock_client = MagicMock()
        mock_client.stream_file.return_value = make_upstream(b"partial", status=206)
        mock_get_client.return_value = mock_client

        self._get(
            "/buildings.pmtiles",
            HTTP_RANGE="bytes=0-9",
            HTTP_AUTHORIZATION="Bearer attacker-token",
            HTTP_X_FORWARDED_HOST="evil.example.com",
        )

        self.assertEqual(
            mock_client.stream_file.call_args.kwargs["headers"],
            {"Range": "bytes=0-9"},
        )

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_unsatisfiable_range_is_passed_through(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.stream_file.return_value = make_upstream(
            b"",
            status=416,
            headers={"Content-Range": f"bytes */{TOTAL_SIZE}"},
        )
        mock_get_client.return_value = mock_client

        response = self._get(
            "/buildings.pmtiles", HTTP_RANGE=f"bytes={TOTAL_SIZE + 1}-"
        )

        self.assertEqual(response.status_code, 416)
        self.assertEqual(response["Content-Range"], f"bytes */{TOTAL_SIZE}")

    @patch("hexa.webapps.views.get_forgejo_client")
    def test_html_is_served_whole_without_range_support(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_file.return_value = b"<html><head></head><body>hi</body></html>"
        mock_get_client.return_value = mock_client

        response = self._get("/", HTTP_RANGE="bytes=0-10")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Accept-Ranges", response)
        mock_client.stream_file.assert_not_called()
