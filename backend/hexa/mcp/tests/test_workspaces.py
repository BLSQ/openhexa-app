from hexa.mcp.tools.workspaces import get_workspace, list_workspaces

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
