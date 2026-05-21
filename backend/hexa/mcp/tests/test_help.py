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
            "    Available topics:\n"
            "    - cli: OpenHEXA comes with a CLI you can install globally on your system. This CLI allows you to interact with the OpenHEXA API and perform various tasks such as creating and managing pipelines, running local jobs and more.\n"
            "    - notebooks-advanced: The notebooks component of OpenHEXA is a customized [Jupyter](https://jupyter.org/) deployment.\n"
            "    - sdk: The OpenHEXA Python SDK is a tool that helps you write code for the OpenHEXA platform.\n"
            "    - static-webapps: Static webapps let you host a small HTML / CSS / JavaScript bundle inside an OpenHEXA workspace and serve it on its own subdomain. They're useful for dashboards, custom data-entry forms, or any front-end that needs to live alongside your pi\n"
            "    - toolbox-dhis2: An utility library to acquire and process data from a DHIS2 instance.\n"
            "    - toolbox-hexa: _⚠️ We now recommend using the [SDK OpenHexa Client](sdk.md#using-the-openhexa-client) instead. It contains plenty of (typed) methods and can be semi-automatically extended by the OpenHexa team. The toolbox client will not be maintained/ext\n"
            "    - toolbox-iaso: Module to fetch data from IASO.\n"
            "    - writing-pipelines: OpenHEXA data pipelines provide a way to help you automate data processing and modelization operations."
        )
        self.assertEqual(get_help_or_doc.__doc__, expected)
