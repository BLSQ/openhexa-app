import uuid
from unittest import mock

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import Feature, FeatureFlag, User
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
            "sabrina@bluesquarehub.com",
            "standardpassword",
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
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_JULIA
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

    def test_generate_workspace_database_new_password_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                mutation generateDatabaseNewPassword($input: GenerateDatabaseNewPasswordInput!) {
                    generateDatabaseNewPassword(input: $input) {
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
            r["data"]["generateDatabaseNewPassword"],
        )

    def test_generate_workspace_database_new_password_denied(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                mutation generateDatabaseNewPassword($input: GenerateDatabaseNewPasswordInput!) {
                    generateDatabaseNewPassword(input: $input) {
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
            r["data"]["generateDatabaseNewPassword"],
        )

    def test_generate_workspace_database_new_password(self):
        self.client.force_login(self.USER_JULIA)
        r = self.run_query(
            """
                mutation generateDatabaseNewPassword($input: GenerateDatabaseNewPasswordInput!) {
                    generateDatabaseNewPassword(input: $input) {
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
            r["data"]["generateDatabaseNewPassword"],
        )
