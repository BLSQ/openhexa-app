from graphql import parse, validate

from config.schema import schema
from hexa.assistant.instructions import (
    _PIPELINE_DOCS,
    _SQL_WIDGETS_DOC,
    _WEBAPP_FILES_DOC,
    PIPELINE_DOC_TOPICS,
    SAVED_QUERY_GQL,
    InstructionSet,
    get_instructions,
)
from hexa.core.test import TestCase
from hexa.mcp.docs import read_doc
from hexa.webapps.models import Webapp
from hexa.webapps.scopes import WebappScopePolicy


class PipelineDocsInstructionsTest(TestCase):
    def test_required_topics_resolve_to_content(self):
        for name in PIPELINE_DOC_TOPICS:
            doc = read_doc(name)
            self.assertIsNotNone(doc, f"missing doc topic '{name}'")
            self.assertTrue(doc["content"].strip(), f"doc topic '{name}' is empty")

    def test_pipeline_docs_block_includes_each_topic(self):
        for name in PIPELINE_DOC_TOPICS:
            self.assertIn(read_doc(name)["content"], _PIPELINE_DOCS)

    def test_create_pipeline_instructions_include_docs(self):
        self.assertIn(_PIPELINE_DOCS, get_instructions(InstructionSet.CREATE_PIPELINE))

    def test_edit_pipeline_instructions_include_docs(self):
        self.assertIn(_PIPELINE_DOCS, get_instructions(InstructionSet.EDIT_PIPELINE))


class WebappDocsInstructionsTest(TestCase):
    def test_create_webapp_instructions_include_docs(self):
        self.assertIn(
            _WEBAPP_FILES_DOC, get_instructions(InstructionSet.CREATE_WEBAPPS)
        )

    def test_edit_webapp_instructions_include_docs(self):
        self.assertIn(_WEBAPP_FILES_DOC, get_instructions(InstructionSet.EDIT_WEBAPP))


class SqlWidgetsInstructionsTest(TestCase):
    def test_sql_widgets_doc_resolves_to_content(self):
        doc = read_doc("sql-widgets")
        self.assertIsNotNone(doc, "missing doc topic 'sql-widgets'")
        self.assertTrue(doc["content"].strip(), "doc topic 'sql-widgets' is empty")

    def test_generate_sql_instructions_include_the_conventions(self):
        instructions = get_instructions(InstructionSet.GENERATE_SQL)
        self.assertIn(_SQL_WIDGETS_DOC, instructions)
        for column in ("bar_label", "bar_quantity", "line_x", "pie_quantity"):
            self.assertIn(column, instructions)

    def test_only_generate_sql_carries_the_conventions(self):
        self.assertNotIn("bar_label", get_instructions(InstructionSet.GENERAL))


class SavedQueryCallInstructionsTest(TestCase):
    """The web app agents get the `executeSavedQuery` call shape inline: left to
    guess it, a model writes `executeSavedQuery(slug:) { results }`, which the
    proxy refuses.
    """

    def test_both_webapp_instruction_sets_show_the_call(self):
        for instruction_set in (
            InstructionSet.CREATE_WEBAPPS,
            InstructionSet.EDIT_WEBAPP,
        ):
            instructions = get_instructions(instruction_set)
            self.assertIn(SAVED_QUERY_GQL, instructions)
            self.assertIn("keyed by column name", instructions)
            self.assertNotIn("executeSavedQuery(slug", instructions)

    def test_only_webapp_instruction_sets_show_the_call(self):
        for instruction_set in (
            InstructionSet.GENERAL,
            InstructionSet.CREATE_PIPELINE,
            InstructionSet.GENERATE_SQL,
        ):
            self.assertNotIn(SAVED_QUERY_GQL, get_instructions(instruction_set))

    def test_the_call_is_valid_and_within_the_database_read_scope(self):
        document = parse(SAVED_QUERY_GQL)
        self.assertEqual(validate(schema, document), [])
        check = WebappScopePolicy([Webapp.OperationScope.DATABASE_READ]).check(document)
        self.assertEqual(check.denied, set())
        self.assertEqual(check.operations, {"executeSavedQuery"})
