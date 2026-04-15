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


def _make_pipeline_stub(zipfile_data=None, version_name="v1"):
    """Build a minimal pipeline-like object for unit-testing propose_pipeline_version."""
    version = MagicMock()
    version.zipfile = zipfile_data
    version.version_name = version_name
    pipeline = MagicMock()
    pipeline.last_version = version if zipfile_data is not None else None
    return pipeline


class ProposePipelineVersionToolTest(TestCase):
    def test_no_existing_version_returns_modified_files(self):
        pipeline = _make_pipeline_stub()
        result = propose_pipeline_version(
            pipeline,
            [ProposedFile(name="pipeline.py", content="print('hello')")],
        )
        self.assertEqual(
            result,
            {"files": [{"name": "pipeline.py", "content": "print('hello')"}]},
        )

    def test_merges_modified_file_into_existing_zip(self):
        zip_data = _make_zipfile(
            ("pipeline.py", "# original"),
            ("utils.py", "# helpers"),
        )
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(
            pipeline,
            [ProposedFile(name="pipeline.py", content="# updated")],
        )
        files = {f["name"]: f["content"] for f in result["files"]}
        self.assertEqual(files["pipeline.py"], "# updated")
        self.assertEqual(files["utils.py"], "# helpers")

    def test_adds_new_file_to_existing_zip(self):
        zip_data = _make_zipfile(("pipeline.py", "# main"))
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(
            pipeline,
            [ProposedFile(name="utils.py", content="# new")],
        )
        files = {f["name"]: f["content"] for f in result["files"]}
        self.assertIn("pipeline.py", files)
        self.assertIn("utils.py", files)

    def test_deletes_file_from_existing_zip(self):
        zip_data = _make_zipfile(
            ("pipeline.py", "# main"),
            ("utils.py", "# helpers"),
        )
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(
            pipeline,
            modified_files=[],
            deleted_files=["utils.py"],
        )
        files = {f["name"] for f in result["files"]}
        self.assertIn("pipeline.py", files)
        self.assertNotIn("utils.py", files)

    def test_empty_modified_files_returns_existing_files_unchanged(self):
        zip_data = _make_zipfile(("pipeline.py", "# main"))
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(pipeline, modified_files=[])
        self.assertEqual(
            result,
            {"files": [{"name": "pipeline.py", "content": "# main"}]},
        )

    def test_no_pipeline_returns_only_modified_files(self):
        result = propose_pipeline_version(
            None,
            [ProposedFile(name="pipeline.py", content="# new")],
        )
        self.assertEqual(
            result,
            {"files": [{"name": "pipeline.py", "content": "# new"}]},
        )


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
