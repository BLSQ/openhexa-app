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
            "    - notebooks-advanced: OpenHEXA notebooks are a customized [Jupyter](https://jupyter.org/) environment preloaded with the OpenHEXA SDK and toolboxes — this guide covers the workspace filesystem, the workspace Postgres from Python and R, and S3/GCS access.\n"
            "    - sdk: The `openhexa.sdk` Python library lets you write pipelines and notebook code against OpenHEXA: a `workspace` helper for files, database, connections, datasets and webapps, plus a typed `OpenHexaClient` for programmatic and GraphQL access.\n"
            "    - static-webapps: Static webapps host an HTML/CSS/JavaScript bundle inside an OpenHEXA workspace, served on its own subdomain, and can query OpenHEXA on behalf of viewing users via a pre-authenticated GraphQL endpoint — great for dashboards and custom forms.\n"
            "    - toolbox-dhis2: The `openhexa.toolbox.dhis2` library connects to a DHIS2 instance with metadata caching, queries org units, data elements and indicators, fetches dataValueSets and analytics, and handles ISO periods and pyramid enrichment.\n"
            "    - toolbox-hexa: DEPRECATED — the `openhexa.toolbox.hexa` GraphQL client is no longer maintained. Use the typed `OpenHexaClient` documented in the [SDK guide](sdk.md#using-the-openhexa-client) instead.\n"
            "    - toolbox-iaso: The `openhexa.toolbox.iaso` `IASO` class authenticates against an IASO instance (staging or production) and fetches projects, organisation units, forms, and form submissions — with optional pandas DataFrame output and filters.\n"
            "    - writing-pipelines: End-to-end guide to authoring OpenHEXA pipelines: `@pipeline`/`@task` DAGs, parallelism and timeouts, typed parameters (datasets, files, secrets, connections, dynamic choices), `workspace.yaml`, GitHub Actions deploys, and Docker runs."
        )
        self.assertEqual(get_help_or_doc.__doc__, expected)
