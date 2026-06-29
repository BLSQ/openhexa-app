from unittest.mock import patch

from hexa.mcp.tools.databases import get_db_schema, get_db_table_schema

from .testutils import MCPTestCase

TABLES = [
    {"name": "patients", "count": 1000, "workspace": object()},
    {"name": "visits", "count": 5000, "workspace": object()},
]

PATIENTS_DEF = {
    "name": "patients",
    "count": 1000,
    "workspace": object(),
    "columns": [
        {"name": "id", "type": "integer"},
        {"name": "name", "type": "text"},
        {"name": "dob", "type": "date"},
    ],
}


class GetDbSchemaTest(MCPTestCase):
    def test_get_db_schema(self):
        with patch(
            "hexa.mcp.tools.databases.get_database_definition", return_value=TABLES
        ):
            result = get_db_schema(
                user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug
            )

        tables = result["tables"]
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]["name"], "patients")
        self.assertEqual(tables[0]["count"], 1000)
        self.assertEqual(tables[1]["name"], "visits")

    def test_get_db_schema_workspace_not_found(self):
        result = get_db_schema(user=self.USER_ADMIN, workspace_slug="nonexistent")
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_schema_no_access(self):
        result = get_db_schema(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_schema_viewer_can_access(self):
        with patch(
            "hexa.mcp.tools.databases.get_database_definition", return_value=TABLES
        ):
            result = get_db_schema(
                user=self.USER_VIEWER, workspace_slug=self.WORKSPACE.slug
            )
        self.assertIn("tables", result)


class GetDbTableSchemaTest(MCPTestCase):
    def test_get_db_table_schema(self):
        with patch(
            "hexa.mcp.tools.databases.get_table_definition", return_value=PATIENTS_DEF
        ):
            result = get_db_table_schema(
                user=self.USER_ADMIN,
                workspace_slug=self.WORKSPACE.slug,
                table_name="patients",
            )

        self.assertEqual(result["name"], "patients")
        self.assertEqual(result["count"], 1000)
        columns = result["columns"]
        self.assertEqual(len(columns), 3)
        self.assertEqual(columns[0], {"name": "id", "type": "integer"})

    def test_get_db_table_schema_table_not_found(self):
        with patch(
            "hexa.mcp.tools.databases.get_table_definition", return_value=None
        ):
            result = get_db_table_schema(
                user=self.USER_ADMIN,
                workspace_slug=self.WORKSPACE.slug,
                table_name="nonexistent",
            )
        self.assertEqual(result, {"error": "Table 'nonexistent' not found"})

    def test_get_db_table_schema_workspace_not_found(self):
        result = get_db_table_schema(
            user=self.USER_ADMIN,
            workspace_slug="nonexistent",
            table_name="patients",
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_table_schema_no_access(self):
        result = get_db_table_schema(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            table_name="patients",
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_table_schema_viewer_can_access(self):
        with patch(
            "hexa.mcp.tools.databases.get_table_definition", return_value=PATIENTS_DEF
        ):
            result = get_db_table_schema(
                user=self.USER_VIEWER,
                workspace_slug=self.WORKSPACE.slug,
                table_name="patients",
            )
        self.assertIn("columns", result)
