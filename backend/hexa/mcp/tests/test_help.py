from hexa.mcp.tools.help import get_help

from .testutils import MCPTestCase


class GetHelpTest(MCPTestCase):
    def test_get_help(self):
        result = get_help(user=self.USER_ADMIN)
        self.assertIn("about", result)
        self.assertIn("common_workflows", result)
        self.assertIn("tips", result)
        self.assertGreater(len(result["tips"]), 0)

    def test_get_help_with_reason(self):
        result = get_help(user=self.USER_ADMIN, reason="unsure which tool to use")
        self.assertIn("about", result)
        self.assertIn("common_workflows", result)
        self.assertIn("tips", result)
