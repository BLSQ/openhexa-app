from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message
from hexa.pipelines.models import Pipeline, PipelineVersion

from ._helpers import _make_tool_call_model, _make_zipfile, _patch_builder
from ._testcase import AgentTestCase


class EditPipelineAgentExtraInstructionsTest(AgentTestCase):
    def _make_agent(self, pipeline=None):
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        if pipeline is not None:
            conversation.linked_object = pipeline
        conversation.save()
        with _patch_builder(TestModel()):
            return EditPipelineAgent(conversation)

    def test_no_pipeline_returns_empty_string(self):
        agent = self._make_agent(pipeline=None)
        self.assertEqual(agent._extra_instructions(), "")

    def test_pipeline_without_version_includes_name_and_code(self):
        pipeline = Pipeline.objects.create(
            code="my-pipeline", name="My Pipeline", workspace=self.workspace
        )
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertIn("My Pipeline", instructions)
        self.assertIn("my-pipeline", instructions)

    def test_pipeline_description_is_included(self):
        pipeline = Pipeline.objects.create(
            code="desc-pipeline",
            name="Described Pipeline",
            description="Loads data from S3.",
            workspace=self.workspace,
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertIn("Loads data from S3.", agent._extra_instructions())

    def test_pipeline_without_description_omits_description_line(self):
        pipeline = Pipeline.objects.create(
            code="nodesc-pipeline",
            name="No Description",
            description="",
            workspace=self.workspace,
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertNotIn("Description:", agent._extra_instructions())

    def test_pipeline_with_version_includes_version_name(self):
        pipeline = Pipeline.objects.create(
            code="versioned-pipeline", name="Versioned", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline, user=self.user, name="Initial release"
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertIn("Initial release", agent._extra_instructions())

    def test_pipeline_with_zipfile_includes_file_contents(self):
        pipeline = Pipeline.objects.create(
            code="zip-pipeline", name="Zip Pipeline", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline,
            user=self.user,
            zipfile=_make_zipfile(("pipeline.py", "print('hello')")),
        )
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertIn("pipeline.py", instructions)
        self.assertIn("print('hello')", instructions)

    def test_pipeline_with_multiple_files_includes_all(self):
        pipeline = Pipeline.objects.create(
            code="multi-pipeline", name="Multi File", workspace=self.workspace
        )
        PipelineVersion.objects.create(
            pipeline=pipeline,
            user=self.user,
            zipfile=_make_zipfile(
                ("pipeline.py", "# main"),
                ("utils.py", "# helpers"),
            ),
        )
        agent = self._make_agent(pipeline=pipeline)
        instructions = agent._extra_instructions()
        self.assertIn("pipeline.py", instructions)
        self.assertIn("utils.py", instructions)

    def test_pipeline_is_injected_into_context(self):
        pipeline = Pipeline.objects.create(
            code="ctx-pipeline", name="Context Pipeline", workspace=self.workspace
        )
        agent = self._make_agent(pipeline=pipeline)
        self.assertIn("pipeline", agent._context)
        self.assertEqual(agent._context["pipeline"], pipeline)

    def test_no_pipeline_context_pipeline_is_none(self):
        agent = self._make_agent(pipeline=None)
        self.assertIn("pipeline", agent._context)
        self.assertIsNone(agent._context["pipeline"])


class EditPipelineAgentToolCallTest(AgentTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.pipeline = Pipeline.objects.create(
            code="tool-pipeline", name="Tool Pipeline", workspace=cls.workspace
        )

    def test_propose_pipeline_version_call_is_persisted(self):
        files_arg = [{"name": "pipeline.py", "content": "print('v2')"}]
        model = _make_tool_call_model(
            "propose_pipeline_version", {"modified_files": files_arg}
        )
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        conversation.linked_object = self.pipeline
        conversation.save()
        with _patch_builder(model):
            agent = EditPipelineAgent(conversation)
        agent.run("Update the pipeline")
        invocation = (
            conversation.messages.filter(role=Message.Role.ASSISTANT)
            .first()
            .tool_invocations.first()
        )
        self.assertEqual(invocation.tool_name, "propose_pipeline_version")
        self.assertTrue(invocation.success)
        self.assertIn("files", invocation.tool_output)
        self.assertEqual(invocation.tool_output["files"][0]["name"], "pipeline.py")
