from hexa.assistant.instructions import (
    _PIPELINE_DOCS,
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
