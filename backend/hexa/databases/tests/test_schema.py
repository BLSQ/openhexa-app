import functools
import uuid
from unittest import mock

from django.conf import settings

from hexa.core.test import GraphQLTestCase
from hexa.databases.tests.helpers import seed_demo_table
from hexa.databases.utils import (
    TableRowsPage,
    execute_database_query,
)
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class DatabaseTest(GraphQLTestCase):
    USER_SABRINA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SUPERUSER = User.objects.create_user(
            "superuser@bluesquarehub.com", "superuserpassword", is_superuser=True
        )

        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com", "standardpassword"
        )
        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword"
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
        WorkspaceMembership.objects.create(
            user=cls.USER_JULIA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def test_get_database_credentials_empty(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                query workspaceById($slug: String!) {
                    workspace(slug: $slug) {
                        database {
                           credentials {
                            username
                           }
                        }
                    }
                }
                """,
            {"slug": str(self.WORKSPACE.slug)},
        )
        self.assertEqual(
            {"credentials": None},
            r["data"]["workspace"]["database"],
        )

    def test_get_database_credentials(self):
        self.client.force_login(self.USER_JULIA)
        with mock.patch(
            "hexa.workspaces.models.get_db_server_credentials"
        ) as mocked_get_db_server_credentials:
            host = "127.0.0.1"
            port = 5432
            mocked_get_db_server_credentials.return_value = {
                "host": host,
                "port": port,
                "username": self.WORKSPACE.db_name,
                "name": self.WORKSPACE.db_name,
            }
            r = self.run_query(
                """
                query workspaceById($slug: String!) {
                    workspace(slug: $slug) {
                        database {
                            credentials {
                                dbName
                                username
                                port
                                host
                                url
                                password
                           }
                        }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug)},
            )
            self.assertEqual(
                {
                    "dbName": self.WORKSPACE.db_name,
                    "username": self.WORKSPACE.db_name,
                    "port": port,
                    "host": f"{self.WORKSPACE.slug}.{settings.WORKSPACES_DATABASE_PROXY_HOST}",
                    "url": self.WORKSPACE.db_url,
                    "password": self.WORKSPACE.db_password,
                },
                r["data"]["workspace"]["database"]["credentials"],
            )

    def test_get_database_tables_empty(self):
        self.client.force_login(self.USER_SABRINA)
        with mock.patch(
            "hexa.databases.schema.get_database_definition"
        ) as mocked_get_database_definition:
            mocked_get_database_definition.return_value = []
            r = self.run_query(
                """
                query workspaceById($slug: String!) {
                    workspace(slug: $slug) {
                        database {
                           tables {
                             items {
                                name
                            }
                          }
                        }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug)},
            )

            self.assertEqual(
                {"tables": {"items": []}}, r["data"]["workspace"]["database"]
            )

    def test_get_database_tables(self):
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        count = 2
        with mock.patch(
            "hexa.databases.schema.get_database_definition"
        ) as mocked_get_database_definition:
            mocked_get_database_definition.return_value = [
                {"workspace": self.WORKSPACE, "name": table_name, "count": count}
            ]

            r = self.run_query(
                """
                query workspaceById($slug: String!) {
                    workspace(slug: $slug) {
                        database {
                           tables {
                             items {
                                name
                                count
                            }
                          }
                        }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug)},
            )
            self.assertEqual(
                {"tables": {"items": [{"name": table_name, "count": count}]}},
                r["data"]["workspace"]["database"],
            )

    def test_get_database_table_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        with mock.patch(
            "hexa.databases.schema.get_table_definition"
        ) as mocked_get_database_definition:
            mocked_get_database_definition.return_value = {}
            r = self.run_query(
                """
                query workspaceById($slug: String!,$tableName:String!) {
                    workspace(slug: $slug) {
                        database {
                           table(name:$tableName) {
                              name
                              count
                          }
                        }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug), "tableName": table_name},
            )

            self.assertEqual(
                {"table": None},
                r["data"]["workspace"]["database"],
            )

    def test_get_database_table(self):
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        count = 2
        schema = {"name": "id", "type": "int"}
        sample = [{"id": str(uuid.uuid4())}]
        table = {
            "workspace": self.WORKSPACE,
            "name": table_name,
            "count": count,
            "columns": [schema],
        }
        with mock.patch(
            "hexa.databases.schema.get_table_definition"
        ) as mocked_get_table_definition:
            mocked_get_table_definition.return_value = table

            with mock.patch(
                "hexa.databases.schema.get_table_sample_data"
            ) as mocked_get_table_sample_data:
                mocked_get_table_sample_data.return_value = sample

                r = self.run_query(
                    """
                    query workspaceById($slug:String!, $tableName:String!) {
                        workspace(slug: $slug) {
                            database {
                            table(name:$tableName) {
                                name
                                count
                                columns {
                                    name
                                    type
                                }
                                sample
                            }
                            }
                        }
                    }
                   """,
                    {"slug": str(self.WORKSPACE.slug), "tableName": table_name},
                )

            self.assertEqual(
                {
                    "table": {
                        "name": table_name,
                        "count": count,
                        "columns": [schema],
                        "sample": sample,
                    }
                },
                r["data"]["workspace"]["database"],
            )

    def test_get_database_table_rows(self):
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        count = 2
        schema = {"name": "id", "type": "int"}
        table = {
            "workspace": self.WORKSPACE,
            "name": table_name,
            "count": count,
            "columns": [schema],
        }
        with mock.patch(
            "hexa.databases.schema.get_table_definition"
        ) as mocked_get_table_definition:
            mocked_get_table_definition.return_value = table

            with mock.patch(
                "hexa.databases.schema.get_table_rows"
            ) as mocked_get_table_rows:
                mocked_get_table_rows.return_value = TableRowsPage(
                    page=1,
                    has_previous=False,
                    has_next=False,
                    items=[],
                )

                r = self.run_query(
                    """
                    query workspaceById($slug:String!, $tableName:String!) {
                        workspace(slug: $slug) {
                            database {
                                table(name: $tableName) {
                                    name
                                    rows(orderBy: "unknown", direction: ASC page: 1, perPage: 2) {
                                         hasNextPage
                                         hasPreviousPage
                                         pageNumber
                                         items
                                    }
                                }
                            }
                        }
                    }
                   """,
                    {
                        "slug": str(self.WORKSPACE.slug),
                        "tableName": table_name,
                    },
                )

            self.assertEqual(
                {
                    "table": {
                        "name": table_name,
                        "rows": {
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                            "pageNumber": 1,
                            "items": [],
                        },
                    }
                },
                r["data"]["workspace"]["database"],
            )

    def _execute_sql(self, query, max_rows=None):
        r = self.run_query(
            """
            query workspaceById($slug: String!, $query: String!, $maxRows: Int) {
                workspace(slug: $slug) {
                    database {
                        executeSQL(query: $query, maxRows: $maxRows) {
                            success
                            errors
                            errorMessage
                            columns
                            rows
                            rowCount
                            truncated
                        }
                    }
                }
            }
            """,
            {
                "slug": str(self.WORKSPACE.slug),
                "query": query,
                "maxRows": max_rows,
            },
        )
        return r["data"]["workspace"]["database"]["executeSQL"]

    def test_execute_sql(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])

        result = self._execute_sql("SELECT id, label FROM demo ORDER BY id")

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

    def test_execute_sql_truncated(self):
        self.client.force_login(self.USER_SABRINA)
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])

        result = self._execute_sql("SELECT id FROM demo ORDER BY id", max_rows=2)

        self.assertTrue(result["success"])
        self.assertEqual([{"id": 1}, {"id": 2}], result["rows"])
        self.assertEqual(2, result["rowCount"])
        self.assertTrue(result["truncated"])

    def test_execute_sql_error(self):
        self.client.force_login(self.USER_SABRINA)

        result = self._execute_sql("SELCT 1")

        self.assertFalse(result["success"])
        self.assertEqual(["QUERY_ERROR"], result["errors"])
        self.assertIn("syntax error", result["errorMessage"])
        self.assertIsNone(result["rows"])

    def test_execute_sql_permission_denied(self):
        self.client.force_login(self.USER_SABRINA)
        with mock.patch("hexa.databases.permissions.run_query", return_value=False):
            result = self._execute_sql("SELECT 1")

        self.assertFalse(result["success"])
        self.assertEqual(["PERMISSION_DENIED"], result["errors"])
        self.assertIsNone(result["rows"])

    def test_execute_sql_statement_timeout(self):
        self.client.force_login(self.USER_SABRINA)
        # Run the real query against the real database, but with a low timeout so
        # the statement is canceled quickly instead of waiting the full sleep.
        fast_execute = functools.partial(execute_database_query, timeout_ms=100)
        with mock.patch("hexa.databases.schema.execute_database_query", fast_execute):
            result = self._execute_sql("SELECT pg_sleep(3);")

        self.assertFalse(result["success"])
        self.assertEqual(["QUERY_TIMEOUT"], result["errors"])
        self.assertIn("statement timeout", result["errorMessage"])

    def test_generate_workspace_database_new_password_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                mutation generateNewDatabasePassword($input: GenerateNewDatabasePasswordInput!) {
                    generateNewDatabasePassword(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"workspaceSlug": str(uuid.uuid4())}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["NOT_FOUND"],
            },
            r["data"]["generateNewDatabasePassword"],
        )

    def test_generate_workspace_database_new_password_denied(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                mutation generateNewDatabasePassword($input: GenerateNewDatabasePasswordInput!) {
                    generateNewDatabasePassword(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"workspaceSlug": str(self.WORKSPACE.slug)}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["generateNewDatabasePassword"],
        )

    def test_generate_workspace_database_new_password(self):
        self.client.force_login(self.USER_JULIA)
        r = self.run_query(
            """
                mutation generateNewDatabasePassword($input: GenerateNewDatabasePasswordInput!) {
                    generateNewDatabasePassword(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"workspaceSlug": str(self.WORKSPACE.slug)}},
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["generateNewDatabasePassword"],
        )
