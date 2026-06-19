from unittest import mock

from psycopg2.errors import InsufficientPrivilege, QueryCanceled, UndefinedTable
from psycopg2.extras import DictRow

from hexa.core.test import TestCase
from hexa.databases.tests.helpers import seed_demo_table
from hexa.databases.utils import (
    MultipleStatementsError,
    OrderByDirectionEnum,
    TableNotFound,
    TableRowsPage,
    delete_table,
    execute_database_query,
    get_database_definition,
    get_row_count,
    get_table_definition,
    get_table_rows,
)
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
)


class DictRowMock:
    def __init__(self, my_dict):
        # we need to set these 2 attributes so that
        # it auto populates our indexes
        self.index = {key: i for i, key in enumerate(my_dict)}
        self.description = my_dict


def dictrow_from_dict(my_dict):
    # this is just a little helper function
    # so you don't always need to go through
    # the steps to recreate a DictRow
    fake_cursor = DictRowMock(my_dict)

    dict_row = DictRow(fake_cursor)

    for k, v in my_dict.items():
        dict_row[k] = v

    return dict_row


class GetRowCountTest(TestCase):
    def test_small_table_uses_accurate_count(self):
        cursor = mock.MagicMock()
        cursor.fetchone.return_value = {"row_count": 42}

        result = get_row_count(cursor, "my_table", reltuples=100)

        self.assertEqual(42, result)
        cursor.execute.assert_called_once()

    def test_large_table_uses_estimate(self):
        cursor = mock.MagicMock()

        result = get_row_count(cursor, "my_table", reltuples=500_000)

        self.assertEqual(500_000, result)
        cursor.execute.assert_not_called()

    def test_unanalyzed_small_table_uses_accurate_count(self):
        cursor = mock.MagicMock()
        cursor.fetchone.side_effect = [
            {"QUERY PLAN": [{"Plan": {"Plan Rows": 50}}]},
            {"row_count": 55},
        ]

        result = get_row_count(cursor, "my_table", reltuples=-1)

        self.assertEqual(55, result)
        self.assertEqual(2, cursor.execute.call_count)

    def test_unanalyzed_large_table_uses_estimate(self):
        cursor = mock.MagicMock()
        cursor.fetchone.return_value = {"QUERY PLAN": [{"Plan": {"Plan Rows": 50_000}}]}

        result = get_row_count(cursor, "my_table", reltuples=-1)

        self.assertEqual(50_000, result)
        self.assertEqual(1, cursor.execute.call_count)


class DatabaseUtilsTest(TestCase):
    USER_SABRINA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SUPERUSER = User.objects.create_user(
            "superuser@bluesquarehub.com", "superuserpassword", is_superuser=True
        )

        cls.DB1 = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db1"
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com", "standardpassword"
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SUPERUSER,
            name="Test Workspace",
            description="Test workspace",
            countries=[],
        )

    @mock.patch("psycopg2.connect")
    def test_get_database_tables_empty(self, mock_connect):
        mock_context_object = mock_connect.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = []

        result = get_database_definition(self.WORKSPACE)
        self.assertEqual(0, len(result))

    @mock.patch("psycopg2.connect")
    def test_get_database_tables(self, mock_connect):
        table_name = "database_tutorial"
        row_count = 2
        table = {"name": table_name, "columns": [], "count": row_count}

        mock_context_object = mock_connect.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [table]
        cursor.fetchone.return_value = {"row_count": 2}
        result = get_database_definition(self.WORKSPACE)

        self.assertEqual(1, len(result))
        self.assertEqual(table_name, result[0]["name"])

    @mock.patch("psycopg2.connect")
    def test_get_table_definition(self, mock_connect):
        table_name = "database_tutorial"
        row_count = 2
        schema = {"name": "id", "type": "int"}
        table = {
            "name": table_name,
            "columns": [schema],
            "count": row_count,
            "workspace": self.WORKSPACE,
        }

        mock_context_object = mock_connect.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [schema]
        cursor.fetchone.return_value = {"row_count": row_count}

        result = get_table_definition(self.WORKSPACE, table_name)

        self.assertEqual(table, result)

    @mock.patch("psycopg2.connect")
    def test_get_table_definition_not_found(self, mock_get_database_connection):
        table_name = "database_tutorial"

        mock_context_object = mock_get_database_connection.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = []

        result = get_table_definition(self.WORKSPACE, table_name)

        self.assertIsNone(result)

    @mock.patch("psycopg2.connect")
    def test_get_paginate_table_rows(self, mock_connect):
        mock_context_object = mock_connect.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value

        items = [{"id": x} for x in range(10)]

        cursor.fetchall.return_value = items

        # Exact number as the page size
        self.assertEqual(
            TableRowsPage(has_previous=False, has_next=False, page=1, items=items),
            get_table_rows(
                self.WORKSPACE,
                "database_tutorial",
                "id",
                OrderByDirectionEnum.ASC,
                1,
                10,
            ),
        )

        # First page; page < items
        self.assertEqual(
            TableRowsPage(has_previous=False, has_next=True, page=1, items=items[0:5]),
            get_table_rows(
                self.WORKSPACE,
                "database_tutorial",
                "id",
                OrderByDirectionEnum.ASC,
                1,
                5,
            ),
        )
        # Second page
        cursor.fetchall.return_value = items[5:]
        self.assertEqual(
            TableRowsPage(has_previous=True, has_next=False, page=2, items=items[5:]),
            get_table_rows(
                self.WORKSPACE,
                "database_tutorial",
                "id",
                OrderByDirectionEnum.ASC,
                2,
                5,
            ),
        )

        # Page in between
        cursor.fetchall.return_value = items[3:7]
        self.assertEqual(
            TableRowsPage(has_previous=True, has_next=True, page=2, items=items[3:6]),
            get_table_rows(
                self.WORKSPACE,
                "database_tutorial",
                "id",
                OrderByDirectionEnum.ASC,
                2,
                3,
            ),
        )

    @mock.patch("psycopg2.connect")
    def test_delete_database_table_not_found(self, mock_connect):
        table_name = "database_tutorial"

        mock_context_object = mock_connect.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.execute.side_effect = UndefinedTable

        with self.assertRaises(TableNotFound):
            delete_table(self.WORKSPACE, table_name)

    @mock.patch("psycopg2.connect")
    def test_delete_database_table(self, mock_connect):
        table_name = "database_tutorial"

        mock_context_object = mock_connect.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.execute.return_value = "DROP TABLE"

        delete_table(self.WORKSPACE, table_name)

    def test_execute_database_query(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])

        result = execute_database_query(
            self.WORKSPACE, "SELECT id, label FROM demo ORDER BY id"
        )

        self.assertEqual(
            {
                "columns": ["id", "label"],
                "rows": [
                    {"id": 1, "label": "a"},
                    {"id": 2, "label": "b"},
                    {"id": 3, "label": "c"},
                ],
                "row_count": 3,
                "truncated": False,
            },
            result,
        )

    def test_execute_database_query_truncates_to_max_rows(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])

        result = execute_database_query(
            self.WORKSPACE, "SELECT id FROM demo ORDER BY id", max_rows=2
        )

        self.assertEqual([{"id": 1}, {"id": 2}], result["rows"])
        self.assertEqual(2, result["row_count"])
        self.assertTrue(result["truncated"])

    def test_execute_database_query_defaults_to_50_rows(self):
        result = execute_database_query(
            self.WORKSPACE, "SELECT generate_series(1, 100) AS id"
        )

        self.assertEqual(50, result["row_count"])
        self.assertTrue(result["truncated"])

    def test_execute_database_query_caps_at_hard_limit(self):
        with self.settings(WORKSPACE_DATABASE_QUERY_MAX_ROWS=2):
            result = execute_database_query(
                self.WORKSPACE,
                "SELECT generate_series(1, 100) AS id",
                max_rows=1000,
            )

        self.assertEqual(2, result["row_count"])
        self.assertTrue(result["truncated"])

    def test_execute_database_query_no_result_set(self):
        result = execute_database_query(self.WORKSPACE, "SET search_path TO public")

        self.assertEqual(
            {"columns": [], "rows": [], "row_count": 0, "truncated": False}, result
        )

    def test_execute_database_query_is_read_only(self):
        seed_demo_table(self.WORKSPACE, [(1, "a")])
        write_statements = [
            "INSERT INTO demo (id, label) VALUES (2, 'b');",
            "UPDATE demo SET label = 'x';",
            "DELETE FROM demo;",
            "DROP TABLE demo;",
            "CREATE TABLE should_not_exist (id int);",
        ]
        for statement in write_statements:
            with self.subTest(statement=statement):
                with self.assertRaises(InsufficientPrivilege):
                    execute_database_query(self.WORKSPACE, statement)

    def test_execute_database_query_enforces_statement_timeout(self):
        # pg_sleep runs far longer than the timeout, so the statement is cancelled.
        with self.assertRaises(QueryCanceled):
            execute_database_query(
                self.WORKSPACE, "SELECT pg_sleep(3);", timeout_ms=100
            )

    def test_execute_database_query_rejects_multiple_statements(self):
        with self.assertRaises(MultipleStatementsError):
            execute_database_query(self.WORKSPACE, "SELECT 1; SELECT 2")

    def test_execute_database_query_allows_trailing_semicolon(self):
        result = execute_database_query(self.WORKSPACE, "SELECT 1 AS id;")

        self.assertEqual(1, result["row_count"])
        self.assertEqual([{"id": 1}], result["rows"])
