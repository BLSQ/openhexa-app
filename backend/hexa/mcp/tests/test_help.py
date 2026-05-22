from hexa.mcp.tools.help import get_help_or_doc

from .testutils import MCPTestCase


class GetHelpOrDocTest(MCPTestCase):
    def test_overview_when_no_topic(self):
        result = get_help_or_doc(user=self.USER_ADMIN)
        self.assertIn("about", result)
        self.assertIn("common_workflows", result)
        self.assertIn("tips", result)
        self.assertGreater(len(result["tips"]), 0)
        self.assertIn("docs", result)
        self.assertIsInstance(result["docs"], list)

    def test_overview_with_reason(self):
        result = get_help_or_doc(
            user=self.USER_ADMIN, reason="unsure which tool to use"
        )
        self.assertIn("about", result)
        self.assertIn("docs", result)

    def test_unknown_topic_returns_error_with_available_topics(self):
        result = get_help_or_doc(user=self.USER_ADMIN, topic="does-not-exist")
        self.assertEqual(result["error"], "Unknown topic 'does-not-exist'.")
        self.assertEqual(
            set(result["available_topics"]),
            {
                "cli",
                "notebooks-advanced",
                "sdk",
                "static-webapps",
                "toolbox-dhis2",
                "toolbox-hexa",
                "toolbox-iaso",
                "writing-pipelines",
            },
        )

    def test_known_topic_returns_full_md_content(self):
        result = get_help_or_doc(user=self.USER_ADMIN, topic="writing-pipelines")
        self.assertEqual(result["name"], "writing-pipelines")
        self.assertEqual(result["title"], "Writing OpenHEXA Pipelines")
        self.assertIn(
            "OpenHEXA data pipelines provide a way to help you automate data processing",
            result["content"],
        )
        self.assertIn("## Quickstart", result["content"])

    def test_docstring_lists_curated_topics(self):
        expected = (
            "Call this tool when you are stuck, unsure what to do next, or need guidance on OpenHEXA.\n"
            "\n"
            "- Leave topic empty for an overview (orientation, common workflows, tips). Pass a reason\n"
            "  describing what you are stuck on (e.g. 'unsure which tool to use', 'pipeline failed',\n"
            "  'cannot find dataset').\n"
            "- Pass a topic name to fetch that doc page in full. Reason is optional here.\n"
            "\n"
            "\n"
            "    Available topics: cli, notebooks-advanced, sdk, static-webapps, toolbox-dhis2, toolbox-hexa, toolbox-iaso, writing-pipelines."
        )
        self.assertEqual(get_help_or_doc.__doc__, expected)
