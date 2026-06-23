from unittest.mock import MagicMock, patch

from hexa.assistant.agents.edit_webapp_agent import ProposedFile, propose_webapp_version
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.core.test import TestCase
from hexa.git.enums import FileEncoding
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp
from hexa.workspaces.models import Workspace


def _make_webapp_stub(files=None):
    webapp = MagicMock(spec=GitWebapp)
    webapp.get_files.return_value = files or []
    return webapp


def _make_file_entry(path, content, encoding=FileEncoding.TEXT):
    return {"path": path, "content": content, "encoding": encoding}


class ProposeWebappChangesToolTest(TestCase):
    def test_no_existing_files_returns_modified_files(self):
        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Hello</h1>")],
        )
        self.assertEqual(
            result,
            {"files": [{"path": "index.html", "content": "<h1>Hello</h1>"}]},
        )

    def test_merges_modified_file_into_existing_files(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Original</h1>"),
                _make_file_entry("style.css", "body {}"),
            ]
        )
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Updated</h1>")],
        )
        files = {f["path"]: f["content"] for f in result["files"]}
        self.assertEqual(files["index.html"], "<h1>Updated</h1>")
        self.assertEqual(files["style.css"], "body {}")

    def test_adds_new_file_to_existing_webapp(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>"),
            ]
        )
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="about.html", content="<h1>About</h1>")],
        )
        files = {f["path"] for f in result["files"]}
        self.assertIn("index.html", files)
        self.assertIn("about.html", files)

    def test_deletes_file_from_existing_webapp(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>"),
                _make_file_entry("old.html", "<h1>Old</h1>"),
            ]
        )
        result = propose_webapp_version(
            webapp,
            modified_files=[],
            deleted_files=["old.html"],
        )
        files = {f["path"] for f in result["files"]}
        self.assertIn("index.html", files)
        self.assertNotIn("old.html", files)

    def test_empty_modified_files_returns_existing_files_unchanged(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>"),
            ]
        )
        result = propose_webapp_version(webapp, modified_files=[])
        self.assertEqual(
            result,
            {"files": [{"path": "index.html", "content": "<h1>Home</h1>"}]},
        )

    def test_binary_files_are_excluded(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>", FileEncoding.TEXT),
                _make_file_entry("logo.png", "binarydata", FileEncoding.BASE64),
            ]
        )
        result = propose_webapp_version(webapp, modified_files=[])
        files = {f["path"] for f in result["files"]}
        self.assertIn("index.html", files)
        self.assertNotIn("logo.png", files)


class ProposeWebappChangesWithPendingProposalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "webapp-tool-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Tool Test Workspace", description=""
            )

    def _make_conversation(self):
        return Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_WEBAPP,
        )

    def _make_pending_invocation(self, conversation, files):
        message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=[],
        )
        return ToolInvocation.objects.create(
            message=message,
            tool_name="propose_webapp_version",
            tool_call_id="call-pending-001",
            tool_input={},
            success=True,
            proposal_pending=True,
            tool_output={"files": files},
        )

    def test_pending_proposal_is_used_as_base_instead_of_live_files(self):
        conversation = self._make_conversation()
        pending_files = [
            {"path": "index.html", "content": "<h1>Pending</h1>"},
            {"path": "style.css", "content": "body { color: red; }"},
        ]
        self._make_pending_invocation(conversation, pending_files)

        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Updated</h1>")],
            conversation=conversation,
        )
        files = {f["path"]: f["content"] for f in result["files"]}
        self.assertEqual(files["index.html"], "<h1>Updated</h1>")
        self.assertEqual(files["style.css"], "body { color: red; }")
        webapp.get_files.assert_not_called()

    def test_no_pending_proposal_falls_back_to_live_files(self):
        conversation = self._make_conversation()
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Live</h1>"),
            ]
        )
        result = propose_webapp_version(
            webapp, modified_files=[], conversation=conversation
        )
        files = {f["path"] for f in result["files"]}
        self.assertIn("index.html", files)
        webapp.get_files.assert_called_once()
