from hexa.assistant.instructions import (
    _PIPELINE_DOCS,
    _SQL_WIDGETS_DOC,
    PIPELINE_DOC_TOPICS,
    InstructionSet,
    get_instructions,
)
from hexa.core.test import TestCase
from hexa.mcp.docs import read_doc


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
