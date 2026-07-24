import json
import threading
from pathlib import Path
from unittest import mock

from asgiref.sync import async_to_sync
from django.test import override_settings
from django.urls import reverse
from psycopg2.errors import QueryCanceled

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

# Shared with the frontend (DataStudioEditor/downloadQueryCsv.test.ts): the one
# source of truth for the download-handshake constants the two tiers must agree
# on. Asserting the view against it here (and the frontend against it there)
# turns a silent handshake break into a failing test. See the fixture's comment.
DOWNLOAD_CONTRACT = json.loads(
    (Path(__file__).parent / "fixtures" / "download_contract.json").read_text()
)
COOKIE_PREFIX = DOWNLOAD_CONTRACT["cookiePrefix"]
FIELD_QUERY = DOWNLOAD_CONTRACT["fields"]["query"]
FIELD_TOKEN = DOWNLOAD_CONTRACT["fields"]["token"]


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

    @staticmethod
    def _collect(response):
        # The download is an async stream (what actually streams under ASGI), so
        # consume it through an event loop rather than a plain join.
        async def collect():
            return b"".join([chunk async for chunk in response.streaming_content])

        return async_to_sync(collect)()

    def _download(self, query):
        response = self.client.post(self._url(), {"query": query})
        return self._collect(response) if response.streaming else None

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
        content = self._collect(response).decode("utf-8")
        self.assertEqual(
            UTF8_BOM + "id,label\r\n1,a\r\n2,b\r\n",
            content,
        )

    def test_download_is_not_gzipped_because_it_is_an_async_stream(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])

        response = self.client.post(
            self._url(),
            {"query": "SELECT id, label FROM demo ORDER BY id"},
            HTTP_ACCEPT_ENCODING="gzip",
        )

        # SSEAwareGZipMiddleware leaves async streams uncompressed: Django 5.2
        # would gzip them one member per chunk, which browsers can't reliably
        # decode. So even though the client accepts gzip, the body is plain CSV.
        self.assertIsNone(response.get("Content-Encoding"))
        self.assertEqual(
            'attachment; filename="query-results.csv"',
            response.headers["Content-Disposition"],
        )
        self.assertEqual(
            UTF8_BOM + "id,label\r\n1,a\r\n2,b\r\n",
            self._collect(response).decode("utf-8"),
        )

    def test_download_sets_the_per_token_cookie_on_success(self):
        # This is the backend half of the cross-tier handshake binding: it posts
        # under the contract's field names and asserts the "download began" cookie
        # the frontend polls for. Sourcing every literal from DOWNLOAD_CONTRACT is
        # what makes a rename on either tier fail a test instead of the handshake
        # breaking silently (the frontend is bound to the same file).
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a")])

        response = self.client.post(
            self._url(),
            {FIELD_QUERY: "SELECT id FROM demo", FIELD_TOKEN: "tok-123"},
        )
        self._collect(response)

        # The token is carried by the cookie name so concurrent downloads each
        # get their own signal; the value is just a presence flag.
        self.assertEqual("1", response.cookies[f"{COOKIE_PREFIX}tok-123"].value)

    def test_download_cookie_secure_follows_the_session_setting(self):
        # The Secure flag tracks SESSION_COOKIE_SECURE: on under TLS (prod), off over
        # plain HTTP (dev), where the browser would drop a Secure cookie and silently
        # break the poll. Guards against re-hardcoding the flag either way.
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a")])

        def cookie_secure():
            response = self.client.post(
                self._url(),
                {FIELD_QUERY: "SELECT id FROM demo", FIELD_TOKEN: "tok-123"},
            )
            self._collect(response)
            return response.cookies[f"{COOKIE_PREFIX}tok-123"]["secure"]

        with override_settings(SESSION_COOKIE_SECURE=False):
            self.assertFalse(cookie_secure())
        with override_settings(SESSION_COOKIE_SECURE=True):
            self.assertTrue(cookie_secure())

    def test_download_ignores_a_malformed_token(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a")])

        response = self.client.post(
            self._url(),
            {FIELD_QUERY: "SELECT id FROM demo", FIELD_TOKEN: "bad token;drop"},
        )
        self._collect(response)

        self.assertEqual(200, response.status_code)
        self.assertFalse(
            any(name.startswith(COOKIE_PREFIX) for name in response.cookies)
        )

    def test_download_error_does_not_set_the_token_cookie(self):
        self.client.force_login(self.USER_SABRINA)

        response = self.client.post(
            self._url(),
            {FIELD_QUERY: "SELECT 1; SELECT 2", FIELD_TOKEN: "tok-123"},
        )

        self.assertEqual(400, response.status_code)
        self.assertNotIn(f"{COOKIE_PREFIX}tok-123", response.cookies)

    def test_download_failing_mid_stream_aborts_the_stream_and_is_logged(self):
        self.client.force_login(self.USER_SABRINA)

        # A query that starts returning rows and then fails (e.g. a statement
        # timeout on a large scan). With a streamed response the 200 and headers
        # are already on the wire, so — unlike the buffered design — this cannot
        # become a clean 400: the download ends truncated. What we guarantee
        # instead is that the failure is recorded server-side.
        def failing_rows():
            yield [{"id": 1}]
            raise QueryCanceled("canceling statement due to statement timeout")

        with mock.patch(
            "hexa.databases.views.stream_database_query",
            return_value=(["id"], failing_rows()),
        ):
            response = self.client.post(
                self._url(),
                {FIELD_QUERY: "SELECT id FROM demo", FIELD_TOKEN: "tok-123"},
            )

            # Streaming began: the status is 200 and the "download began" signal
            # is already set and can no longer be retracted.
            self.assertEqual(200, response.status_code)
            self.assertEqual("1", response.cookies[f"{COOKIE_PREFIX}tok-123"].value)

            with self.assertLogs("hexa.databases.views", level="WARNING") as logs:
                with self.assertRaises(QueryCanceled):
                    self._collect(response)
        self.assertTrue(any("aborted" in line for line in logs.output))

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

    def test_download_streams_across_multiple_server_side_batches(self):
        self.client.force_login(self.USER_SABRINA)
        # generate_series returns more rows than one server-side batch
        # (DOWNLOAD_QUERY_BATCH_SIZE = 2000), so the stream must fetch several
        # times mid-download — each fetch run off the event loop via sync_to_async
        # on the (blocking) psycopg2 cursor. This exercises that cross-thread path,
        # which the small-result tests above do not.
        content = self._download("SELECT generate_series(1, 5000) AS id")

        lines = content.decode("utf-8").lstrip(UTF8_BOM).strip().split("\r\n")
        self.assertEqual("id", lines[0])
        self.assertEqual(5000, len(lines) - 1)
        self.assertEqual("5000", lines[-1])

    def test_download_neutralises_formula_injection(self):
        self.client.force_login(self.USER_SABRINA)

        content = self._download("SELECT '=1+1' AS v").decode("utf-8")

        self.assertEqual(UTF8_BOM + "v\r\n'=1+1\r\n", content)

    def test_download_rejects_when_export_slots_are_exhausted(self):
        self.client.force_login(self.USER_SABRINA)
        # A pool with no free slot stands in for "too many exports already running".
        exhausted = threading.BoundedSemaphore(1)
        exhausted.acquire()
        with mock.patch("hexa.databases.views._EXPORT_SLOTS", exhausted):
            response = self.client.post(self._url(), {"query": "SELECT 1"})
        self.assertEqual(429, response.status_code)

    def test_download_releases_the_slot_after_a_successful_export(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a")])
        slots = threading.BoundedSemaphore(1)
        with mock.patch("hexa.databases.views._EXPORT_SLOTS", slots):
            response = self.client.post(self._url(), {"query": "SELECT id FROM demo"})
            self._collect(response)
            self.assertEqual(200, response.status_code)
            # The single slot must be free again, or exports would wedge after one run.
            self.assertTrue(slots.acquire(blocking=False))

    def test_download_releases_the_slot_after_an_error(self):
        self.client.force_login(self.USER_SABRINA)
        slots = threading.BoundedSemaphore(1)
        with mock.patch("hexa.databases.views._EXPORT_SLOTS", slots):
            response = self.client.post(self._url(), {"query": "SELECT 1; SELECT 2"})
            self.assertEqual(400, response.status_code)
            # A failed export must not permanently consume a slot.
            self.assertTrue(slots.acquire(blocking=False))

    def test_download_releases_the_slot_when_the_stream_fails_midway(self):
        self.client.force_login(self.USER_SABRINA)
        slots = threading.BoundedSemaphore(1)

        def failing_rows():
            yield [{"id": 1}]
            raise QueryCanceled("canceling statement due to statement timeout")

        with (
            mock.patch("hexa.databases.views._EXPORT_SLOTS", slots),
            mock.patch(
                "hexa.databases.views.stream_database_query",
                return_value=(["id"], failing_rows()),
            ),
        ):
            response = self.client.post(self._url(), {"query": "SELECT id FROM demo"})
            with self.assertRaises(QueryCanceled):
                self._collect(response)
            # The slot is tied to the stream's lifetime (released in on_finish), so
            # a mid-stream failure must still hand it back rather than leak it.
            self.assertTrue(slots.acquire(blocking=False))

    # The disconnect path — Django calling response.close() without the stream
    # being consumed — is covered at the unit level in core/tests/test_csv.py
    # (test_close_runs_cleanup_when_the_stream_was_never_consumed). It is not
    # re-tested here because response.close() fires the request_finished signal,
    # which closes the test's own DB connection mid-transaction and breaks the
    # rest of the class; release_export itself is already exercised by the
    # success and error slot-release tests above.

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
