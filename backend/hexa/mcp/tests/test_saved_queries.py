from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.mcp.tools.saved_queries import (
    create_saved_query,
    get_saved_query,
    list_saved_queries,
    update_saved_query,
)
from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole

from .testutils import MCPTestCase


# USER_ADMIN is a superuser and therefore sees and edits every query, so the
# visibility rules need a plain workspace editor to be observable.
class SavedQueryTestCase(MCPTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.USER_EDITOR = User.objects.create_user("editor@openhexa.org", "password")
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )


class ListSavedQueriesTest(SavedQueryTestCase):
    def test_list_saved_queries(self):
        create_result = create_saved_query(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name="Listed query",
            content="SELECT 1",
            description="Counts things",
        )
        self.assertTrue(create_result["success"], create_result["errors"])

        result = list_saved_queries(
            user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug
        )
        page = result["savedQueries"]
        self.assertEqual(page["totalItems"], 1)
        self.assertEqual(page["pageNumber"], 1)
        item = page["items"][0]
        self.assertEqual(item["id"], create_result["savedQuery"]["id"])
        self.assertEqual(item["name"], "Listed query")
        self.assertNotIn("content", item)
        self.assertEqual(item["visibility"], "PRIVATE")
        self.assertTrue(item["permissions"]["update"])

    def test_list_saved_queries_filters_by_query(self):
        for name in ["Sales report", "Stock levels"]:
            create_saved_query(
                user=self.USER_ADMIN,
                workspace_slug=self.WORKSPACE.slug,
                name=name,
                content="SELECT 1",
            )

        result = list_saved_queries(
            user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug, query="sales"
        )
        self.assertEqual(result["savedQueries"]["totalItems"], 1)
        self.assertEqual(result["savedQueries"]["items"][0]["name"], "Sales report")

    def test_list_saved_queries_hides_others_private_queries(self):
        create_saved_query(
            user=self.USER_VIEWER,
            workspace_slug=self.WORKSPACE.slug,
            name="Viewer private",
            content="SELECT 1",
        )
        create_saved_query(
            user=self.USER_VIEWER,
            workspace_slug=self.WORKSPACE.slug,
            name="Viewer shared",
            content="SELECT 2",
            visibility=SavedQueryVisibility.WORKSPACE,
        )

        result = list_saved_queries(
            user=self.USER_EDITOR, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(
            [q["name"] for q in result["savedQueries"]["items"]], ["Viewer shared"]
        )

    def test_list_saved_queries_no_access(self):
        result = list_saved_queries(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result, {"error": "Workspace not found"})


class GetSavedQueryTest(SavedQueryTestCase):
    def test_get_saved_query(self):
        saved_query = SavedQuery.objects.create(
            workspace=self.WORKSPACE,
            created_by=self.USER_VIEWER,
            name="Shared query",
            content="SELECT 1",
            description="A description",
            visibility=SavedQueryVisibility.WORKSPACE,
        )

        result = get_saved_query(
            user=self.USER_EDITOR, saved_query_slug=saved_query.slug
        )
        self.assertEqual(result["id"], str(saved_query.id))
        self.assertEqual(result["slug"], "shared-query")
        self.assertEqual(result["name"], "Shared query")
        self.assertEqual(result["content"], "SELECT 1")
        self.assertEqual(result["description"], "A description")
        self.assertEqual(result["visibility"], "WORKSPACE")
        self.assertEqual(result["workspace"]["slug"], self.WORKSPACE.slug)
        self.assertTrue(result["permissions"]["update"])
        self.assertFalse(result["permissions"]["updateVisibility"])

    def test_get_saved_query_private_hidden_from_others(self):
        saved_query = SavedQuery.objects.create(
            workspace=self.WORKSPACE,
            created_by=self.USER_VIEWER,
            name="Private query",
            content="SELECT 1",
        )

        result = get_saved_query(
            user=self.USER_EDITOR, saved_query_slug=saved_query.slug
        )
        self.assertEqual(result, {"error": "Saved query not found"})

    def test_get_saved_query_not_found(self):
        result = get_saved_query(user=self.USER_ADMIN, saved_query_slug="nope")
        self.assertEqual(result, {"error": "Saved query not found"})


class CreateSavedQueryTest(SavedQueryTestCase):
    def test_create_saved_query(self):
        result = create_saved_query(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name="My query",
            content="SELECT * FROM table",
            description="A description",
            visibility=SavedQueryVisibility.WORKSPACE,
        )
        self.assertTrue(result["success"], result["errors"])
        saved_query = result["savedQuery"]
        self.assertEqual(saved_query["name"], "My query")
        self.assertEqual(saved_query["slug"], "my-query")
        self.assertEqual(saved_query["content"], "SELECT * FROM table")
        self.assertEqual(saved_query["description"], "A description")
        self.assertEqual(saved_query["visibility"], "WORKSPACE")

        db_query = SavedQuery.objects.get(id=saved_query["id"])
        self.assertEqual(db_query.workspace, self.WORKSPACE)
        self.assertEqual(db_query.created_by, self.USER_ADMIN)

    def test_create_saved_query_defaults_to_private(self):
        result = create_saved_query(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name="My query",
            content="SELECT 1",
        )
        self.assertTrue(result["success"], result["errors"])
        self.assertEqual(result["savedQuery"]["visibility"], "PRIVATE")

    def test_create_saved_query_no_access(self):
        result = create_saved_query(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            name="My query",
            content="SELECT 1",
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["WORKSPACE_NOT_FOUND"])
        self.assertIsNone(result["savedQuery"])


class UpdateSavedQueryTest(SavedQueryTestCase):
    def setUp(self):
        super().setUp()
        self.SAVED_QUERY = SavedQuery.objects.create(
            workspace=self.WORKSPACE,
            created_by=self.USER_VIEWER,
            name="Original",
            content="SELECT 1",
            description="Original description",
        )

    def test_update_saved_query(self):
        result = update_saved_query(
            user=self.USER_VIEWER,
            saved_query_id=str(self.SAVED_QUERY.id),
            name="Renamed",
            content="SELECT 2",
            description="New description",
            visibility=SavedQueryVisibility.WORKSPACE,
        )
        self.assertTrue(result["success"], result["errors"])
        self.assertEqual(result["savedQuery"]["name"], "Renamed")
        self.assertEqual(result["savedQuery"]["content"], "SELECT 2")
        self.assertEqual(result["savedQuery"]["description"], "New description")
        self.assertEqual(result["savedQuery"]["visibility"], "WORKSPACE")
        self.SAVED_QUERY.refresh_from_db()
        self.assertEqual(self.SAVED_QUERY.name, "Renamed")
        self.assertEqual(self.SAVED_QUERY.content, "SELECT 2")
        self.assertEqual(self.SAVED_QUERY.visibility, SavedQueryVisibility.WORKSPACE)

    def test_update_saved_query_only_provided_fields(self):
        result = update_saved_query(
            user=self.USER_VIEWER,
            saved_query_id=str(self.SAVED_QUERY.id),
            content="SELECT 2",
        )
        self.assertTrue(result["success"], result["errors"])
        self.SAVED_QUERY.refresh_from_db()
        self.assertEqual(self.SAVED_QUERY.name, "Original")
        self.assertEqual(self.SAVED_QUERY.content, "SELECT 2")
        self.assertEqual(self.SAVED_QUERY.description, "Original description")
        self.assertEqual(self.SAVED_QUERY.visibility, SavedQueryVisibility.PRIVATE)

    def test_update_saved_query_private_hidden_from_others(self):
        result = update_saved_query(
            user=self.USER_EDITOR,
            saved_query_id=str(self.SAVED_QUERY.id),
            name="Renamed",
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["SAVED_QUERY_NOT_FOUND"])

    def test_update_saved_query_visibility_only_by_author(self):
        self.SAVED_QUERY.visibility = SavedQueryVisibility.WORKSPACE
        self.SAVED_QUERY.save()

        result = update_saved_query(
            user=self.USER_EDITOR,
            saved_query_id=str(self.SAVED_QUERY.id),
            visibility=SavedQueryVisibility.PRIVATE,
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["PERMISSION_DENIED"])
        self.SAVED_QUERY.refresh_from_db()
        self.assertEqual(self.SAVED_QUERY.visibility, SavedQueryVisibility.WORKSPACE)

    def test_update_shared_saved_query_by_editor(self):
        self.SAVED_QUERY.visibility = SavedQueryVisibility.WORKSPACE
        self.SAVED_QUERY.save()

        result = update_saved_query(
            user=self.USER_EDITOR,
            saved_query_id=str(self.SAVED_QUERY.id),
            content="SELECT 3",
        )
        self.assertTrue(result["success"], result["errors"])
        self.SAVED_QUERY.refresh_from_db()
        self.assertEqual(self.SAVED_QUERY.content, "SELECT 3")

    def test_update_saved_query_not_found(self):
        result = update_saved_query(
            user=self.USER_ADMIN,
            saved_query_id="00000000-0000-0000-0000-000000000000",
            name="Renamed",
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["SAVED_QUERY_NOT_FOUND"])
