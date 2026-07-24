from django.core.cache import cache

from hexa.core.test import TestCase
from hexa.databases.tests.helpers import seed_demo_table
from hexa.mcp.tools.databases import get_db_schema, get_db_table_schema
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


# These tools query the workspace database through the GraphQL layer, so unlike
# MCPTestCase (which patches database creation away) we need a workspace backed
# by a real database that we can seed with a demo table.
class DatabaseToolsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@openhexa.org", "password", is_superuser=True
        )
        cls.USER_VIEWER = User.objects.create_user("viewer@openhexa.org", "password")
        cls.USER_OUTSIDER = User.objects.create_user(
            "outsider@openhexa.org", "password"
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Test Workspace",
            description="A test workspace",
        )

        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def setUp(self):
        # The schema cache (LocMemCache) is a process-global store that isn't
        # rolled back with the per-test DB transaction, so tests that hit the
        # same (workspace, page, per_page, with_columns, with_counts) key would
        # otherwise silently read another test's cached result.
        cache.clear()


class GetDbSchemaTest(DatabaseToolsTestCase):
    def test_get_db_schema(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])

        result = get_db_schema(user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug)

        self.assertEqual([{"name": "demo", "count": 3}], result["tables"])
        self.assertEqual(1, result["pageNumber"])
        self.assertEqual(1, result["totalPages"])
        self.assertEqual(1, result["totalItems"])

    def test_get_db_schema_pagination(self):
        seed_demo_table(self.WORKSPACE, [(1, "a")])
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")], table_name="demo_2")

        result = get_db_schema(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            page=2,
            per_page=1,
        )

        self.assertEqual([{"name": "demo_2", "count": 2}], result["tables"])
        self.assertEqual(2, result["pageNumber"])
        self.assertEqual(2, result["totalPages"])
        self.assertEqual(2, result["totalItems"])

    def test_get_db_schema_workspace_not_found(self):
        result = get_db_schema(user=self.USER_ADMIN, workspace_slug="nonexistent")
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_schema_no_access(self):
        result = get_db_schema(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_schema_viewer_can_access(self):
        seed_demo_table(self.WORKSPACE, [(1, "a")])

        result = get_db_schema(
            user=self.USER_VIEWER, workspace_slug=self.WORKSPACE.slug
        )

        # The workspace database is not rolled back between tests, so other
        # tables seeded by sibling tests may still exist.
        self.assertIn({"name": "demo", "count": 1}, result["tables"])


class GetDbTableSchemaTest(DatabaseToolsTestCase):
    def test_get_db_table_schema(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])

        result = get_db_table_schema(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            table_name="demo",
        )

        self.assertEqual(
            {
                "name": "demo",
                "count": 3,
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "label", "type": "text"},
                ],
            },
            result,
        )

    def test_get_db_table_schema_table_not_found(self):
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
            table_name="demo",
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_table_schema_no_access(self):
        result = get_db_table_schema(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            table_name="demo",
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_get_db_table_schema_viewer_can_access(self):
        seed_demo_table(self.WORKSPACE, [(1, "a")])

        result = get_db_table_schema(
            user=self.USER_VIEWER,
            workspace_slug=self.WORKSPACE.slug,
            table_name="demo",
        )

        self.assertEqual("demo", result["name"])
        self.assertEqual(2, len(result["columns"]))
