from unittest import mock

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_postgresql.models import Database
from hexa.user_management.models import User


class DatabaseTest(GraphQLTestCase):
    USER_SABRINA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        cls.DB1 = Database.objects.create(
            hostname="host", username="user", password="pwd", database="db1"
        )

    def test_get_database_table_db_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            query databaseTable($tableId:String!, $databaseId:String!) {
                databaseTable(id: $tableId, databaseId: $databaseId) {
                    name
                    totalCount
                }
            }
            """,
            {
                "tableId": "test_db",
                "databaseId": "test",
            },
        )
        self.assertIsNone(r["data"]["databaseTable"])

    def test_get_database_table_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            query databaseTable($tableId:String!, $databaseId:String!) {
                databaseTable(id: $tableId, databaseId: $databaseId) {
                    name
                    totalCount
                }
            }
            """,
            {"tableId": "test", "databaseId": self.DB1.database},
        )

        self.assertEqual(None, r["data"]["databaseTable"])

    @mock.patch("hexa.databases.schema.get_database_tables_summary")
    def test_get_database_table(self, mocked_get_database_tables_summary):
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        total_count = 2
        mocked_get_database_tables_summary.return_value = [
            {"name": table_name, "total_count": total_count}
        ]
        r = self.run_query(
            """
                query databaseTable($tableId:String!, $databaseId:String!) {
                    databaseTable(id: $tableId, databaseId: $databaseId) {
                        name
                        totalCount
                    }
                }
                """,
            {
                "tableId": table_name,
                "databaseId": self.DB1.database,
            },
        )
        self.assertEqual(
            {"name": table_name, "totalCount": total_count},
            r["data"]["databaseTable"],
        )

    def test_get_database_table_columns(
        self,
    ):
        self.client.force_login(self.USER_SABRINA)
        table_name = "test_table"
        total_count = 2
        column = {"name": "id", "type": "int"}

        with mock.patch(
            "hexa.databases.schema.get_database_tables_summary"
        ) as mocked_get_database_tables_summary:
            mocked_get_database_tables_summary.return_value = [
                {"name": table_name, "total_count": total_count, "database": self.DB1}
            ]
            with mock.patch(
                "hexa.databases.schema.get_table_summary"
            ) as mocked_get_table_summary:
                mocked_get_table_summary.return_value = [column]
                r = self.run_query(
                    """
                    query databaseTable($tableId:String!, $databaseId:String!) {
                        databaseTable(id: $tableId, databaseId: $databaseId) {
                            name
                            totalCount
                            columns {
                                name
                                type
                            }
                        }
                    }
                """,
                    {
                        "tableId": table_name,
                        "databaseId": self.DB1.database,
                    },
                )
                self.assertEqual(
                    {
                        "name": table_name,
                        "totalCount": total_count,
                        "columns": [column],
                    },
                    r["data"]["databaseTable"],
                )
