import io
import zipfile
from unittest.mock import MagicMock, patch

from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.edit_pipeline_agent import (
    EditPipelineAgent,
    ProposedFile,
    propose_pipeline_version,
)
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.core.test import TestCase
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


def _patch_builder(test_model):
    mock_builder = MagicMock()
    mock_builder.model_api_name = "test"
    mock_builder.provider_id = "test"
    mock_builder.build.return_value = test_model
    return patch(
        "hexa.assistant.agents.base.AiModelBuilder.from_conversation",
        return_value=mock_builder,
    )


def _make_zipfile(*files: tuple[str, str]) -> bytes:
    """Build an in-memory zip containing the given (name, content) pairs."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files:
            zf.writestr(name, content)
    return buf.getvalue()


class ProposePipelineVersionToolTest(TestCase):
    def test_returns_files_list(self):
        result = propose_pipeline_version(
            [ProposedFile(name="pipeline.py", content="print('hello')")]
        )
        self.assertEqual(
            result,
            {"files": [{"name": "pipeline.py", "content": "print('hello')"}]},
        )

    def test_returns_multiple_files(self):
        result = propose_pipeline_version(
            [
                ProposedFile(name="pipeline.py", content="# main"),
                ProposedFile(name="utils.py", content="# utils"),
            ]
        )
        self.assertEqual(len(result["files"]), 2)
        names = [f["name"] for f in result["files"]]
        self.assertIn("pipeline.py", names)
        self.assertIn("utils.py", names)

    def test_empty_file_list(self):
        result = propose_pipeline_version([])
        self.assertEqual(result, {"files": []})


class EditPipelineAgentExtraInstructionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "edit-instructions@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Edit Instructions WS", description=""
            )

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
        instructions = agent._extra_instructions()
        self.assertIn("Initial release", instructions)

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
