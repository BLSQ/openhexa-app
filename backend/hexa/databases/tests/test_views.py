from unittest import mock

from django.urls import reverse

from hexa.core.csv import UTF8_BOM
from hexa.core.test import TestCase
from hexa.databases.tests.helpers import seed_demo_table
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class DownloadQueryCsvViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_SUPERUSER = User.objects.create_user(
            "superuser@bluesquarehub.com", "superuserpassword", is_superuser=True
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com", "standardpassword"
        )
        cls.USER_OUTSIDER = User.objects.create_user(
            "outsider@bluesquarehub.com", "outsiderpassword"
        )
        cls.DB1 = Database.objects.create(
            hostname="host",
            username="user",
            password="pwd",
            database="hexa-explore-demo",
        )
        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SUPERUSER,
            name="Test Workspace",
            description="Test workspace",
            countries=[],
        )
        setattr(cls.WORKSPACE, "database", cls.DB1)
        WorkspaceMembership.objects.create(
            user=cls.USER_SABRINA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def _url(self, slug=None):
        return reverse(
            "databases:download_query_csv",
            args=[slug or str(self.WORKSPACE.slug)],
        )

    def _download(self, query):
        response = self.client.post(self._url(), {"query": query})
        return b"".join(response.streaming_content) if response.streaming else None

    def test_download_streams_full_result_as_csv(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])

        response = self.client.post(
            self._url(), {"query": "SELECT id, label FROM demo ORDER BY id"}
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.streaming)
        self.assertEqual(
            'attachment; filename="query-results.csv"',
            response.headers["Content-Disposition"],
        )
        content = b"".join(response.streaming_content).decode("utf-8")
        self.assertEqual(
            UTF8_BOM + "id,label\r\n1,a\r\n2,b\r\n",
            content,
        )

    def test_download_ignores_the_interactive_row_cap(self):
        self.client.force_login(self.USER_SABRINA)
        # More rows than the interactive editor's default cap (50), to prove the
        # download returns the whole result set rather than a capped page.
        rows = [(i, f"label-{i}") for i in range(1, 121)]
        seed_demo_table(self.WORKSPACE, rows)

        content = self._download("SELECT id FROM demo ORDER BY id")

        data_lines = content.decode("utf-8").strip().split("\r\n")
        # header + 120 rows
        self.assertEqual(121, len(data_lines))
        self.assertEqual("id", data_lines[0].lstrip(UTF8_BOM))
        self.assertEqual("120", data_lines[-1])

    def test_download_neutralises_formula_injection(self):
        self.client.force_login(self.USER_SABRINA)

        content = self._download("SELECT '=1+1' AS v").decode("utf-8")

        self.assertEqual(UTF8_BOM + "v\r\n'=1+1\r\n", content)

    def test_download_denied_without_permission(self):
        self.client.force_login(self.USER_SABRINA)
        with mock.patch("hexa.databases.permissions.run_query", return_value=False):
            response = self.client.post(self._url(), {"query": "SELECT 1"})
        self.assertEqual(403, response.status_code)

    def test_download_rejects_multiple_statements(self):
        self.client.force_login(self.USER_SABRINA)
        response = self.client.post(self._url(), {"query": "SELECT 1; SELECT 2"})
        self.assertEqual(400, response.status_code)

    def test_download_rejects_invalid_sql(self):
        self.client.force_login(self.USER_SABRINA)
        response = self.client.post(self._url(), {"query": "SELCT 1"})
        self.assertEqual(400, response.status_code)

    def test_download_requires_a_query(self):
        self.client.force_login(self.USER_SABRINA)
        response = self.client.post(self._url(), {"query": "   "})
        self.assertEqual(400, response.status_code)

    def test_download_rejects_get(self):
        self.client.force_login(self.USER_SABRINA)
        response = self.client.get(self._url())
        self.assertEqual(405, response.status_code)

    def test_download_unknown_workspace_returns_404(self):
        self.client.force_login(self.USER_OUTSIDER)
        response = self.client.post(self._url(), {"query": "SELECT 1"})
        self.assertEqual(404, response.status_code)

    def test_download_requires_login(self):
        response = self.client.post(self._url(), {"query": "SELECT 1"})
        self.assertEqual(302, response.status_code)
