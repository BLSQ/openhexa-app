from hexa.mcp.tools.workspaces import get_workspace, list_workspaces, update_workspace

from .testutils import MCPTestCase


class ListWorkspacesTest(MCPTestCase):
    def test_list_workspaces(self):
        result = list_workspaces(user=self.USER_ADMIN)
        workspaces = result["workspaces"]
        self.assertEqual(workspaces["totalItems"], 1)
        self.assertEqual(workspaces["items"][0]["slug"], self.WORKSPACE.slug)

    def test_list_workspaces_filter(self):
        result = list_workspaces(user=self.USER_ADMIN, query="nonexistent")
        self.assertEqual(result["workspaces"]["totalItems"], 0)

    def test_list_workspaces_filter_matching(self):
        result = list_workspaces(user=self.USER_ADMIN, query="Test")
        self.assertEqual(result["workspaces"]["totalItems"], 1)
        self.assertEqual(result["workspaces"]["items"][0]["slug"], self.WORKSPACE.slug)

    def test_list_workspaces_outsider(self):
        result = list_workspaces(user=self.USER_OUTSIDER)
        self.assertEqual(result["workspaces"]["totalItems"], 0)

    def test_list_workspaces_pagination(self):
        result = list_workspaces(user=self.USER_ADMIN, page=1, per_page=1)
        self.assertEqual(result["workspaces"]["pageNumber"], 1)


class GetWorkspaceTest(MCPTestCase):
    def test_get_workspace(self):
        result = get_workspace(user=self.USER_ADMIN, slug=self.WORKSPACE.slug)
        workspace = result["workspace"]
        self.assertEqual(workspace["slug"], self.WORKSPACE.slug)
        self.assertEqual(workspace["name"], "Test Workspace")
        self.assertEqual(workspace["description"], "A test workspace")

    def test_get_workspace_not_found(self):
        result = get_workspace(user=self.USER_ADMIN, slug="nonexistent")
        self.assertIsNone(result["workspace"])

    def test_get_workspace_no_access(self):
        result = get_workspace(user=self.USER_OUTSIDER, slug=self.WORKSPACE.slug)
        self.assertIsNone(result["workspace"])


class UpdateWorkspaceTest(MCPTestCase):
    def test_update_name(self):
        result = update_workspace(
            user=self.USER_ADMIN, slug=self.WORKSPACE.slug, name="Renamed Workspace"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["workspace"]["name"], "Renamed Workspace")

    def test_update_description(self):
        result = update_workspace(
            user=self.USER_ADMIN,
            slug=self.WORKSPACE.slug,
            description="Updated description",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["workspace"]["description"], "Updated description")

    def test_update_docker_image(self):
        result = update_workspace(
            user=self.USER_ADMIN,
            slug=self.WORKSPACE.slug,
            docker_image="eu.gcr.io/my-org/my-image:latest",
        )
        self.assertTrue(result["success"])
        self.assertEqual(
            result["workspace"]["dockerImage"], "eu.gcr.io/my-org/my-image:latest"
        )

    def test_update_countries(self):
        result = update_workspace(
            user=self.USER_ADMIN,
            slug=self.WORKSPACE.slug,
            countries='["US", "FR"]',
        )
        self.assertTrue(result["success"])
        codes = [c["code"] for c in result["workspace"]["countries"]]
        self.assertIn("US", codes)
        self.assertIn("FR", codes)

    def test_update_invalid_countries_json(self):
        result = update_workspace(
            user=self.USER_ADMIN, slug=self.WORKSPACE.slug, countries="not-valid-json"
        )
        self.assertIn("error", result)

    def test_update_permission_denied(self):
        result = update_workspace(
            user=self.USER_VIEWER, slug=self.WORKSPACE.slug, name="Should Fail"
        )
        self.assertFalse(result.get("success", True))

    def test_update_no_fields_is_noop(self):
        result = update_workspace(user=self.USER_ADMIN, slug=self.WORKSPACE.slug)
        self.assertTrue(result["success"])
        self.assertEqual(result["workspace"]["name"], "Test Workspace")
