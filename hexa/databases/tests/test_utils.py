from unittest import mock

from psycopg2.extras import DictRow

from hexa.core.test import TestCase
from hexa.databases.utils import get_database_definition, get_table_definition
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
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

    dick_row = DictRow(fake_cursor)

    for k, v in my_dict.items():
        dick_row[k] = v

    return dick_row


class DatabaseUtilsTest(TestCase):
    USER_SABRINA = None

    def setUp(self):
        self.patch_get_workspace_database = mock.patch(
            "hexa.databases.utils.get_workspace_database", return_value=self.DB1
        )
        self.mock_get_workspace_database = self.patch_get_workspace_database.start()

    def tearDown(self):
        self.patch_get_workspace_database.stop()

    @classmethod
    def setUpTestData(cls):
        cls.DB1 = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db1"
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_SABRINA
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SABRINA,
            name="Test Workspace",
            description="Test workspace",
            countries=[],
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SABRINA,
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

    @mock.patch("psycopg2.connect")
    def test_get_database_tables_empty(self, mock_connect):
        mock_connection = mock_connect.return_value
        mock_context_object = mock_connection.__enter__.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = []

        result = get_database_definition(self.WORKSPACE)
        self.assertEqual(0, len(result))

    @mock.patch("psycopg2.connect")
    def test_get_database_tables(self, mock_connect):
        table_name = "database_tutorial"
        row_count = 2
        table = {"name": table_name, "columns": [], "count": row_count}

        mock_connection = mock_connect.return_value
        mock_context_object = mock_connection.__enter__.return_value
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

        mock_connection = mock_connect.return_value
        mock_context_object = mock_connection.__enter__.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [schema]
        cursor.fetchone.return_value = {"row_count": row_count}

        result = get_table_definition(self.WORKSPACE, table_name)

        self.assertEqual(table, result)

    @mock.patch("psycopg2.connect")
    def test_get_table_definition_not_found(self, mock_connect):
        table_name = "database_tutorial"
        mock_connection = mock_connect.return_value
        mock_context_object = mock_connection.__enter__.return_value
        cursor = mock_context_object.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = []

        result = get_table_definition(self.WORKSPACE, table_name)

        self.assertIsNone(result)
