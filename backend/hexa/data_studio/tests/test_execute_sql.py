import functools
from unittest import mock

from psycopg2 import Error as Psycopg2Error

from hexa.core.test import GraphQLTestCase
from hexa.data_studio.models import QueryLog
from hexa.data_studio.query_runner import (
    _log_executed_query,
    run_and_log_database_query,
)
from hexa.databases.tests.helpers import seed_demo_table
from hexa.databases.utils import execute_database_query
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import PipelineRun
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ExecuteSqlTest(GraphQLTestCase):
    """The Database.executeSQL path: permission check, execution and QueryLog audit.

    Lives here rather than in the databases app because data_studio owns the
    execution path and the audit log; the permission it enforces
    (``databases.run_query``) still belongs to the databases app.
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER_SUPERUSER = User.objects.create_user(
            "superuser@bluesquarehub.com", "superuserpassword", is_superuser=True
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com", "standardpassword"
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

    def _execute_sql(self, query, max_rows=None, origin=None):
        r = self.run_query(
            """
            query workspaceById($slug: String!, $query: String!, $maxRows: Int, $origin: ExecuteSQLOrigin) {
                workspace(slug: $slug) {
                    database {
                        executeSQL(query: $query, maxRows: $maxRows, origin: $origin) {
                            success
                            errors
                            errorMessage
                            columns
                            rows
                            rowCount
                            truncated
                            durationMs
                        }
                    }
                }
            }
            """,
            {
                "slug": str(self.WORKSPACE.slug),
                "query": query,
                "maxRows": max_rows,
                "origin": origin,
            },
        )
        return r["data"]["workspace"]["database"]["executeSQL"]

    def _get_single_query_log(self):
        log = QueryLog.objects.get()
        self.assertEqual(self.WORKSPACE, log.workspace)
        return log

    def test_execute_sql(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])

        result = self._execute_sql("SELECT id, label FROM demo ORDER BY id")

        duration_ms = result.pop("durationMs")
        self.assertIsInstance(duration_ms, int)
        self.assertGreaterEqual(duration_ms, 0)
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "errorMessage": None,
                "columns": ["id", "label"],
                "rows": [{"id": 1, "label": "a"}, {"id": 2, "label": "b"}],
                "rowCount": 2,
                "truncated": False,
            },
            result,
        )
        log = self._get_single_query_log()
        self.assertEqual(self.USER_SABRINA, log.user)
        self.assertEqual("SELECT id, label FROM demo ORDER BY id", log.query)
        self.assertEqual(QueryLog.Status.SUCCESS, log.status)
        self.assertEqual(QueryLog.SQLSTATE_SUCCESS, log.result_code)
        self.assertEqual(QueryLog.Origin.OTHER, log.origin)
        self.assertEqual(2, log.row_count)
        self.assertFalse(log.truncated)
        self.assertIsNotNone(log.duration_ms)

    def test_execute_sql_logs_data_studio_origin(self):
        self.client.force_login(self.USER_SABRINA)

        result = self._execute_sql("SELECT 1", origin="DATA_STUDIO")

        self.assertTrue(result["success"])
        log = self._get_single_query_log()
        self.assertEqual(QueryLog.Origin.DATA_STUDIO, log.origin)

    def test_log_executed_query_resolves_pipeline_run_user(self):
        # Service principals are not User instances; the audit entry must fall
        # back to the human who triggered the run.
        pipeline_run = mock.MagicMock(PipelineRun)
        pipeline_run.user = self.USER_SABRINA
        request = self.mock_request(PipelineRunUser(pipeline_run))

        _log_executed_query(
            request,
            self.WORKSPACE,
            "SELECT 1",
            QueryLog.Origin.OTHER,
            QueryLog.Status.SUCCESS,
        )

        log = self._get_single_query_log()
        self.assertEqual(self.USER_SABRINA, log.user)

    def test_log_executed_query_scheduled_run_has_no_user(self):
        # Scheduled runs have no triggering user; the entry is kept without one.
        pipeline_run = mock.MagicMock(PipelineRun)
        pipeline_run.user = None
        request = self.mock_request(PipelineRunUser(pipeline_run))

        _log_executed_query(
            request,
            self.WORKSPACE,
            "SELECT 1",
            QueryLog.Origin.OTHER,
            QueryLog.Status.SUCCESS,
        )

        log = self._get_single_query_log()
        self.assertIsNone(log.user)

    def test_run_and_log_database_query_logs_before_reraising(self):
        # The resolver relies on this contract: every execution error is
        # logged first, then re-raised to be translated into an API response.
        request = self.mock_request(self.USER_SABRINA)

        with self.assertRaises(Psycopg2Error):
            run_and_log_database_query(
                request, self.WORKSPACE, "SELCT 1", QueryLog.Origin.OTHER
            )

        log = self._get_single_query_log()
        self.assertEqual(QueryLog.Status.ERROR, log.status)
        self.assertEqual("42601", log.result_code)

    def test_execute_sql_log_failure_fails_the_request(self):
        # A failed audit insert means a bug on our side; it must surface as an
        # error instead of being silently swallowed.
        self.client.force_login(self.USER_SABRINA)

        with mock.patch(
            "hexa.data_studio.query_runner.QueryLog.objects.create",
            side_effect=Exception("boom"),
        ):
            r = self.run_query(
                """
                query workspaceById($slug: String!, $query: String!) {
                    workspace(slug: $slug) {
                        database {
                            executeSQL(query: $query) {
                                success
                            }
                        }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug), "query": "SELECT 1"},
            )

        self.assertIn("errors", r)
        self.assertEqual(0, QueryLog.objects.count())

    def test_execute_sql_serializes_binary_values(self):
        self.client.force_login(self.USER_SABRINA)

        result = self._execute_sql("SELECT 'abc'::bytea AS data")

        self.assertTrue(result["success"])
        self.assertEqual([{"data": "\\x616263"}], result["rows"])

    def test_execute_sql_truncated(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])

        result = self._execute_sql("SELECT id FROM demo ORDER BY id", max_rows=2)

        self.assertTrue(result["success"])
        self.assertEqual([{"id": 1}, {"id": 2}], result["rows"])
        self.assertEqual(2, result["rowCount"])
        self.assertTrue(result["truncated"])
        log = self._get_single_query_log()
        self.assertEqual(2, log.row_count)
        self.assertTrue(log.truncated)

    def test_execute_sql_error(self):
        self.client.force_login(self.USER_SABRINA)

        result = self._execute_sql("SELCT 1")

        self.assertFalse(result["success"])
        self.assertEqual(["QUERY_ERROR"], result["errors"])
        self.assertIn("syntax error", result["errorMessage"])
        self.assertIsNone(result["rows"])
        log = self._get_single_query_log()
        self.assertEqual(QueryLog.Status.ERROR, log.status)
        self.assertEqual("42601", log.result_code)
        self.assertIn("syntax error", log.error_message)
        self.assertIsNotNone(log.duration_ms)

    def test_execute_sql_permission_denied(self):
        self.client.force_login(self.USER_SABRINA)
        with mock.patch("hexa.databases.permissions.run_query", return_value=False):
            result = self._execute_sql("SELECT 1")

        self.assertFalse(result["success"])
        self.assertEqual(["PERMISSION_DENIED"], result["errors"])
        self.assertIsNone(result["rows"])
        log = self._get_single_query_log()
        self.assertEqual(QueryLog.Status.DENIED, log.status)
        self.assertEqual(self.USER_SABRINA, log.user)
        self.assertIsNone(log.result_code)
        self.assertIsNone(log.duration_ms)

    def test_execute_sql_statement_timeout(self):
        self.client.force_login(self.USER_SABRINA)
        # Run the real query against the real database, but with a low timeout so
        # the statement is canceled quickly instead of waiting the full sleep.
        fast_execute = functools.partial(execute_database_query, timeout_ms=100)
        with mock.patch("hexa.data_studio.query_runner.execute_database_query", fast_execute):
            result = self._execute_sql("SELECT pg_sleep(3);")

        self.assertFalse(result["success"])
        self.assertEqual(["QUERY_TIMEOUT"], result["errors"])
        self.assertIn("statement timeout", result["errorMessage"])
        log = self._get_single_query_log()
        self.assertEqual(QueryLog.Status.ERROR, log.status)
        # SQLSTATE 57014: query_canceled
        self.assertEqual("57014", log.result_code)

    def test_execute_sql_multiple_statements(self):
        self.client.force_login(self.USER_SABRINA)

        result = self._execute_sql("SELECT 1; SELECT 2")

        self.assertFalse(result["success"])
        self.assertEqual(["MULTIPLE_STATEMENTS"], result["errors"])
        self.assertIsNone(result["rows"])
        log = self._get_single_query_log()
        self.assertEqual(QueryLog.Status.REJECTED, log.status)
        self.assertIsNone(log.result_code)
