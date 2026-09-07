from unittest.mock import MagicMock, patch

from hexa.assistant.agents.edit_pipeline_agent import (
    ProposedFile,
    propose_pipeline_version,
)
from hexa.assistant.agents.proposals import MAX_COMMIT_MESSAGE_LENGTH
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace

from ._helpers import _make_zipfile


def _make_pipeline_stub(zipfile_data=None, version_name="v1"):
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
            {
                "files": [{"name": "pipeline.py", "content": "print('hello')"}],
                "deleted_paths": [],
                "all_paths": ["pipeline.py"],
            },
        )

    def test_deletes_binary_file_by_explicit_path(self):
        zip_data = _make_zipfile(
            ("pipeline.py", "# main"), ("assets/logo.png", "\x00\xff binary")
        )
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(pipeline, deleted_files=["assets/logo.png"])
        self.assertEqual(result["deleted_paths"], ["assets/logo.png"])

    def test_deleting_unknown_path_returns_error(self):
        zip_data = _make_zipfile(("pipeline.py", "# main"))
        pipeline = _make_pipeline_stub(zipfile_data=zip_data)
        result = propose_pipeline_version(pipeline, deleted_files=["nope.py"])
        self.assertIn("error", result)

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
            {
                "files": [{"name": "pipeline.py", "content": "# main"}],
                "deleted_paths": [],
                "all_paths": ["pipeline.py"],
            },
        )

    def test_no_pipeline_returns_only_modified_files(self):
        result = propose_pipeline_version(
            None,
            [ProposedFile(name="pipeline.py", content="# new")],
        )
        self.assertEqual(
            result,
            {
                "files": [{"name": "pipeline.py", "content": "# new"}],
                "deleted_paths": [],
                "all_paths": ["pipeline.py"],
            },
        )


class ProposePipelineVersionCommitMessageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "pipeline-tool-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = create_workspace(
                cls.user, name="Pipeline Tool Test Workspace", description=""
            )

    def _make_conversation(self):
        return Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )

    def _make_pending_invocation(self, conversation, tool_output):
        message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=[],
        )
        return ToolInvocation.objects.create(
            message=message,
            tool_name="propose_pipeline_version",
            tool_call_id="call-pending-001",
            tool_input={},
            success=True,
            proposal_pending=True,
            tool_output=tool_output,
        )

    def test_commit_message_is_returned_with_the_proposal(self):
        result = propose_pipeline_version(
            _make_pipeline_stub(),
            [ProposedFile(name="pipeline.py", content="# new")],
            commit_message="  Add retry logic to the extract task  ",
        )
        self.assertEqual(
            result["commit_message"], "Add retry logic to the extract task"
        )

    def test_no_commit_message_leaves_the_key_out(self):
        result = propose_pipeline_version(
            _make_pipeline_stub(),
            [ProposedFile(name="pipeline.py", content="# new")],
            commit_message="   ",
        )
        self.assertNotIn("commit_message", result)

    def test_too_long_commit_message_returns_error(self):
        result = propose_pipeline_version(
            _make_pipeline_stub(),
            [ProposedFile(name="pipeline.py", content="# new")],
            commit_message="x" * (MAX_COMMIT_MESSAGE_LENGTH + 1),
        )
        self.assertIn("error", result)
        self.assertNotIn("files", result)

    def test_pending_commit_message_carries_over_when_not_restated(self):
        conversation = self._make_conversation()
        self._make_pending_invocation(
            conversation,
            {
                "files": [{"name": "pipeline.py", "content": "# pending"}],
                "deleted_paths": [],
                "all_paths": ["pipeline.py"],
                "commit_message": "Add retry logic to the extract task",
            },
        )
        result = propose_pipeline_version(
            _make_pipeline_stub(),
            [ProposedFile(name="pipeline.py", content="# updated")],
            conversation=conversation,
        )
        self.assertEqual(
            result["commit_message"], "Add retry logic to the extract task"
        )

    def test_new_commit_message_replaces_the_pending_one(self):
        conversation = self._make_conversation()
        self._make_pending_invocation(
            conversation,
            {
                "files": [{"name": "pipeline.py", "content": "# pending"}],
                "deleted_paths": [],
                "all_paths": ["pipeline.py"],
                "commit_message": "Add retry logic to the extract task",
            },
        )
        result = propose_pipeline_version(
            _make_pipeline_stub(),
            [ProposedFile(name="pipeline.py", content="# updated")],
            commit_message="Add retry logic and lower the batch size",
            conversation=conversation,
        )
        self.assertEqual(
            result["commit_message"], "Add retry logic and lower the batch size"
        )
