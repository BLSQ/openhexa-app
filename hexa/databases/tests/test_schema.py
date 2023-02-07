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
        cls.DB1 = Database.objects.create(
            hostname="host",
            username="user",
            password="pwd",
            database="hexa-explore-demo",
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
            mocked_get_database_definition.return_value = {
                "totalItems": 0,
                "totalPages": 0,
                "pageNumber": 0,
                "items": [],
            }
            r = self.run_query(
                """
                query workspaceById($id: UUID!) {
                    workspace(id: $id) {
                        id
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
                {"id": str(self.WORKSPACE.id)},
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
            mocked_get_database_definition.return_value = {
                "totalItems": 1,
                "totalPages": 1,
                "pageNumber": 1,
                "items": [{"name": table_name, "count": count}],
            }

            r = self.run_query(
                """
                query workspaceById($id: UUID!) {
                    workspace(id: $id) {
                        id
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
                {"id": str(self.WORKSPACE.id)},
            )
            self.assertEqual(
                {"tables": {"items": [{"name": table_name, "count": count}]}},
                r["data"]["workspace"]["database"],
            )

    def test_get_database_table_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        count = 2
        with mock.patch(
            "hexa.databases.schema.get_table_definition"
        ) as mocked_get_database_definition:
            mocked_get_database_definition.return_value = {}
            r = self.run_query(
                """
                query workspaceById($id: UUID!,$tableName:String!) {
                    workspace(id: $id) {
                        id
                        database {
                           table(name:$tableName) {
                              name
                              count
                          }
                        }
                    }
                }
                """,
                {"id": str(self.WORKSPACE.id), "tableName": table_name},
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
        sample = [[{"column": "id", "value": str(uuid.uuid4())}]]
        table = {
            "name": table_name,
            "count": count,
            "columns": [schema],
        }
        with mock.patch(
            "hexa.databases.schema.get_table_definition"
        ) as mocked_get_table_definition:
            mocked_get_table_definition.return_value = table
            with mock.patch(
                "hexa.databases.schema.get_table_data"
            ) as mocked_get_table_data:
                mocked_get_table_data.return_value = sample
                r = self.run_query(
                    """
                query workspaceById($id: UUID!,$tableName:String!) {
                    workspace(id: $id) {
                        id
                        database {
                        table(name:$tableName) {
                            name
                            count
                            columns {
                              name
                              type
                            }
                            sample {
                              column
                              value
                            }
                          }
                        }
                    }
                }
                """,
                    {"id": str(self.WORKSPACE.id), "tableName": table_name},
                )
            self.assertEqual(
                {"table": {**table, "sample": sample}},
                r["data"]["workspace"]["database"],
            )
