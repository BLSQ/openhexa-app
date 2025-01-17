from unittest import mock

from psycopg2.errors import UndefinedTable
from psycopg2.extras import DictRow

from hexa.core.test import TestCase
from hexa.databases.utils import (
    OrderByDirectionEnum,
    TableNotFound,
    TableRowsPage,
    delete_table,
    get_database_definition,
    get_table_definition,
    get_table_rows,
)
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


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

    dick_row = DictRow(fake_cursor)

    for k, v in my_dict.items():
        dick_row[k] = v

    return dick_row


class DatabaseUtilsTest(TestCase):
    USER_SABRINA = None

    @classmethod
    def setUpTestData(cls):
        cls.DB1 = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db1"
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com", "standardpassword"
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SABRINA,
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
