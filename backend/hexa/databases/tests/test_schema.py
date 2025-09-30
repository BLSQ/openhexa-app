import uuid
from unittest import mock

from django.conf import settings

from hexa.core.test import GraphQLTestCase
from hexa.databases.utils import TableRowsPage
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
            cls.USER_JULIA,
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

    def test_get_database_table_query_with_filters(self):
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
                "hexa.databases.schema.get_table_query_results"
            ) as mocked_get_table_query_results:
                mocked_get_table_query_results.return_value = TableRowsPage(
                    page=1,
                    has_previous=False,
                    has_next=False,
                    items=[{"id": 1, "active": True}, {"id": 2, "active": False}],
                )

                r = self.run_query(
                    """
                    query workspaceById($slug:String!, $tableName:String!) {
                        workspace(slug: $slug) {
                            database {
                                table(name: $tableName) {
                                    name
                                    query(
                                        filters: [{column: "active", operator: EQ, value: true}],
                                        orderBy: "id",
                                        direction: ASC,
                                        page: 1,
                                        perPage: 2
                                    ) {
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
                    {"slug": str(self.WORKSPACE.slug), "tableName": table_name},
                )
                self.assertEqual(
                    {
                        "name": table_name,
                        "query": {
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                            "pageNumber": 1,
                            "items": [{"id": 1, "active": True}, {"id": 2, "active": False}],
                        },
                    },
                    r["data"]["workspace"]["database"]["table"],
                )

                # Verify the function was called with correct parameters
                mocked_get_table_query_results.assert_called_once()
                call_args = mocked_get_table_query_results.call_args
                self.assertEqual(call_args[1]["workspace"], self.WORKSPACE)
                self.assertEqual(call_args[1]["table_name"], table_name)
                self.assertEqual(len(call_args[1]["filters"]), 1)
                self.assertEqual(call_args[1]["filters"][0]["column"], "active")
                self.assertEqual(call_args[1]["filters"][0]["operator"], "EQ")
                self.assertEqual(call_args[1]["filters"][0]["value"], True)

    def test_get_database_table_query_permission_denied(self):
        """Test that users without database view permission cannot query tables."""
        # Create a user without any workspace permissions
        user_no_permissions = User.objects.create_user(
            "noperm@bluesquarehub.com", "password"
        )
        self.client.force_login(user_no_permissions)
        
        table_name = "test_table"
        with mock.patch(
            "hexa.databases.schema.get_table_definition"
        ) as mocked_get_table_definition:
            mocked_get_table_definition.return_value = {
                "workspace": self.WORKSPACE,
                "name": table_name,
                "count": 0,
                "columns": [],
            }

            r = self.run_query(
                """
                query workspaceById($slug:String!, $tableName:String!) {
                    workspace(slug: $slug) {
                        database {
                            table(name: $tableName) {
                                query(page: 1, perPage: 10) {
                                    pageNumber
                                }
                            }
                        }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug), "tableName": table_name},
            )
            
            # Should get a permission denied error
            self.assertIn("errors", r)
            self.assertTrue(any("permission" in str(error).lower() for error in r["errors"]))

    def test_get_database_table_query_input_validation(self):
        """Test input validation for the query endpoint."""
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        table = {
            "workspace": self.WORKSPACE,
            "name": table_name,
            "count": 0,
            "columns": [],
        }
        
        with mock.patch(
            "hexa.databases.schema.get_table_definition"
        ) as mocked_get_table_definition:
            mocked_get_table_definition.return_value = table

            with mock.patch(
                "hexa.databases.schema.get_table_query_results"
            ) as mocked_get_table_query_results:
                mocked_get_table_query_results.return_value = TableRowsPage(
                    page=1,
                    has_previous=False,
                    has_next=False,
                    items=[],
                )

                # Test with invalid page numbers and per_page values
                r = self.run_query(
                    """
                    query workspaceById($slug:String!, $tableName:String!) {
                        workspace(slug: $slug) {
                            database {
                                table(name: $tableName) {
                                    query(page: -1, perPage: 200) {
                                        pageNumber
                                    }
                                }
                            }
                        }
                    }
                    """,
                    {"slug": str(self.WORKSPACE.slug), "tableName": table_name},
                )
                
                # Should succeed with corrected values
                self.assertIsNone(r.get("errors"))
                
                # Verify the function was called with corrected parameters
                mocked_get_table_query_results.assert_called_once()
                call_args = mocked_get_table_query_results.call_args
                self.assertEqual(call_args[1]["page"], 1)  # Should be corrected from -1
                self.assertEqual(call_args[1]["per_page"], 100)  # Should be capped at 100
