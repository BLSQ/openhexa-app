from unittest.mock import MagicMock, patch

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.assistant.tools.proposals import working_files
from hexa.assistant.tools.webapps import (
    FilePatch,
    ProposedFile,
    glob_webapp_files,
    grep_webapp_files,
    propose_webapp_version,
    read_webapp_file,
)
from hexa.core.test import TestCase
from hexa.core.text_files import TextFiles
from hexa.git.enums import FileEncoding
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp
from hexa.workspaces.tests.testutils import create_workspace


def _make_webapp_stub(files=None):
    webapp = MagicMock(spec=GitWebapp)
    webapp.get_files.return_value = files or []
    return webapp


def _make_file_entry(path, content, encoding: FileEncoding = FileEncoding.TEXT):
    return {
        "path": path,
        "content": content,
        "encoding": encoding,
        "type": "file",
    }


def _make_dir_entry(path):
    return {"path": path, "content": None, "encoding": None, "type": "directory"}


class ProposeWebappChangesToolTest(TestCase):
    def test_no_existing_files_returns_modified_files(self):
        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Hello</h1>")],
        )
        self.assertEqual(
            result,
            {
                "files": [{"path": "index.html", "content": "<h1>Hello</h1>"}],
                "deleted_paths": [],
            },
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

    def test_deletes_binary_file_by_explicit_path(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>"),
                _make_file_entry("logo.png", None, FileEncoding.BASE64),
            ]
        )
        result = propose_webapp_version(
            webapp,
            deleted_files=["logo.png"],
        )
        self.assertEqual(result["deleted_paths"], ["logo.png"])

    def test_deletes_every_file_under_a_directory(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>"),
                _make_dir_entry("assets"),
                _make_file_entry("assets/logo.png", None, FileEncoding.BASE64),
                _make_file_entry("assets/app.css", "body {}"),
            ]
        )
        result = propose_webapp_version(webapp, deleted_files=["assets"])
        self.assertEqual(result["deleted_paths"], ["assets/app.css", "assets/logo.png"])
        self.assertEqual({f["path"] for f in result["files"]}, {"index.html"})

    def test_deleting_unknown_path_returns_error(self):
        webapp = _make_webapp_stub([_make_file_entry("index.html", "<h1>Home</h1>")])
        result = propose_webapp_version(webapp, deleted_files=["nope/"])
        self.assertIn("error", result)
        self.assertIn("nope/", result["error"])

    def test_every_unknown_path_is_reported_at_once(self):
        webapp = _make_webapp_stub([_make_file_entry("index.html", "<h1>Home</h1>")])
        result = propose_webapp_version(
            webapp, deleted_files=["gone.js", "index.html", "missing/"]
        )
        self.assertIn("gone.js", result["error"])
        self.assertIn("missing/", result["error"])
        self.assertNotIn("index.html", result["error"])

    def test_empty_call_returns_error(self):
        webapp = _make_webapp_stub()
        result = propose_webapp_version(webapp)
        self.assertIn("error", result)

    def test_empty_modified_files_with_no_deletions_returns_error(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>"),
            ]
        )
        result = propose_webapp_version(webapp, modified_files=[])
        self.assertIn("error", result)

    def test_file_patch_applies_to_existing_file(self):
        webapp = _make_webapp_stub(
            [_make_file_entry("index.html", "<nav>\n<a>Home</a>\n</nav>")]
        )
        result = propose_webapp_version(
            webapp,
            file_patches=[
                FilePatch(
                    path="index.html",
                    old_string="<a>Home</a>",
                    new_string="<a>Home</a>\n<a>About</a>",
                )
            ],
        )
        files = {f["path"]: f["content"] for f in result["files"]}
        self.assertIn("<a>About</a>", files["index.html"])

    def test_file_patch_old_string_not_found_returns_error(self):
        webapp = _make_webapp_stub([_make_file_entry("index.html", "<nav></nav>")])
        result = propose_webapp_version(
            webapp,
            file_patches=[
                FilePatch(path="index.html", old_string="MISSING", new_string="x")
            ],
        )
        self.assertIn("error", result)
        self.assertIn("old_string not found", result["error"])

    def test_file_patch_on_missing_file_returns_error(self):
        webapp = _make_webapp_stub([])
        result = propose_webapp_version(
            webapp,
            file_patches=[FilePatch(path="ghost.html", old_string="x", new_string="y")],
        )
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])

    def test_file_patches_as_json_string_is_parsed(self):
        webapp = _make_webapp_stub(
            [_make_file_entry("index.html", "<title>Old</title>")]
        )
        patches_json = '[{"path": "index.html", "old_string": "<title>Old</title>", "new_string": "<title>New</title>"}]'
        result = propose_webapp_version(webapp, file_patches=patches_json)
        self.assertNotIn("error", result)
        files = {f["path"]: f["content"] for f in result["files"]}
        self.assertEqual(files["index.html"], "<title>New</title>")

    def test_file_patches_as_invalid_json_string_returns_error(self):
        webapp = _make_webapp_stub([])
        result = propose_webapp_version(webapp, file_patches="not-json")
        self.assertIn("error", result)

    def test_file_patches_alone_satisfy_validation(self):
        webapp = _make_webapp_stub(
            [_make_file_entry("index.html", "<title>Old</title>")]
        )
        result = propose_webapp_version(
            webapp,
            file_patches=[
                FilePatch(
                    path="index.html",
                    old_string="<title>Old</title>",
                    new_string="<title>New</title>",
                )
            ],
        )
        self.assertNotIn("error", result)

    def test_binary_files_are_excluded(self):
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Home</h1>", FileEncoding.TEXT),
                _make_file_entry("logo.png", "binarydata", FileEncoding.BASE64),
            ]
        )
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Updated</h1>")],
        )
        files = {f["path"] for f in result["files"]}
        self.assertIn("index.html", files)
        self.assertNotIn("logo.png", files)


class _PendingProposalTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "webapp-tool-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = create_workspace(
                cls.user, name="Tool Test Workspace", description=""
            )

    def _make_conversation(self):
        return Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_WEBAPP,
        )

    def _make_pending_invocation(
        self, conversation, files, deleted_paths=None, commit_message=None
    ):
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
            tool_output={
                "files": files,
                "deleted_paths": deleted_paths or [],
                **({"commit_message": commit_message} if commit_message else {}),
            },
        )


class ProposeWebappChangesWithPendingProposalTest(_PendingProposalTestCase):
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

    def test_pending_deletions_carry_over_to_the_next_proposal(self):
        conversation = self._make_conversation()
        self._make_pending_invocation(
            conversation,
            [{"path": "index.html", "content": "<h1>Pending</h1>"}],
            deleted_paths=["assets/logo.png"],
        )

        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Updated</h1>")],
            conversation=conversation,
        )
        self.assertEqual(result["deleted_paths"], ["assets/logo.png"])
        webapp.get_files.assert_not_called()

    def test_no_pending_proposal_falls_back_to_live_files(self):
        conversation = self._make_conversation()
        webapp = _make_webapp_stub(
            [
                _make_file_entry("index.html", "<h1>Live</h1>"),
            ]
        )
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Updated</h1>")],
            conversation=conversation,
        )
        files = {f["path"] for f in result["files"]}
        self.assertIn("index.html", files)
        webapp.get_files.assert_called_once()

    def test_commit_message_is_returned_with_the_proposal(self):
        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Hello</h1>")],
            commit_message="  Add a dark theme toggle  ",
        )
        self.assertEqual(result["commit_message"], "Add a dark theme toggle")

    def test_no_commit_message_leaves_the_key_out(self):
        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Hello</h1>")],
            commit_message="   ",
        )
        self.assertNotIn("commit_message", result)

    def test_multi_line_commit_message_is_kept_whole(self):
        webapp = _make_webapp_stub()
        message = (
            "feat(ui): add a dark theme toggle\n"
            "\n"
            "Users reported the dashboard being unreadable in low light."
        )
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Hello</h1>")],
            commit_message=message,
        )
        self.assertEqual(result["commit_message"], message)

    def test_pending_commit_message_carries_over_when_not_restated(self):
        conversation = self._make_conversation()
        self._make_pending_invocation(
            conversation,
            [{"path": "index.html", "content": "<h1>Pending</h1>"}],
            commit_message="Add a dark theme toggle",
        )

        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Updated</h1>")],
            conversation=conversation,
        )
        self.assertEqual(result["commit_message"], "Add a dark theme toggle")

    def test_new_commit_message_replaces_the_pending_one(self):
        conversation = self._make_conversation()
        self._make_pending_invocation(
            conversation,
            [{"path": "index.html", "content": "<h1>Pending</h1>"}],
            commit_message="Add a dark theme toggle",
        )

        webapp = _make_webapp_stub()
        result = propose_webapp_version(
            webapp,
            [ProposedFile(path="index.html", content="<h1>Updated</h1>")],
            commit_message="Add a dark theme toggle and persist the choice",
            conversation=conversation,
        )
        self.assertEqual(
            result["commit_message"], "Add a dark theme toggle and persist the choice"
        )


class WorkingFilesTest(_PendingProposalTestCase):
    saved = TextFiles(
        {"index.html": "<h1>Saved</h1>", "old.js": "old()", "logo.png": None}
    )

    def _working_files(self, conversation):
        return working_files(self.saved, conversation, "propose_webapp_version")

    def test_without_pending_proposal_is_the_saved_version(self):
        files = self._working_files(self._make_conversation())
        self.assertEqual(files.read("index.html")["content"], "<h1>Saved</h1>")

    def test_pending_proposal_overrides_and_deletes_saved_files(self):
        conversation = self._make_conversation()
        self._make_pending_invocation(
            conversation,
            [{"path": "index.html", "content": "<h1>Proposed</h1>"}],
            deleted_paths=["old.js"],
        )
        files = self._working_files(conversation)
        self.assertEqual(files.read("index.html")["content"], "<h1>Proposed</h1>")
        self.assertEqual(files.glob("**")["paths"], ["index.html", "logo.png"])


class WebappFileToolsTest(_PendingProposalTestCase):
    def setUp(self):
        self.webapp = MagicMock(spec=GitWebapp)
        self.webapp.get_text_files.return_value = TextFiles(
            {
                "index.html": "<h1>Saved</h1>",
                "app.js": "function saved() {}",
                "old.js": "old()",
            }
        )
        self.conversation = self._make_conversation()
        self._make_pending_invocation(
            self.conversation,
            [{"path": "app.js", "content": "function proposed() {}"}],
            deleted_paths=["old.js"],
        )

    def test_glob_sees_the_pending_proposal(self):
        result = glob_webapp_files(self.webapp, "*.js", self.conversation)
        self.assertEqual(result["paths"], ["app.js"])

    def test_grep_sees_the_pending_proposal(self):
        result = grep_webapp_files(
            self.webapp,
            "function",
            output_mode="content",
            conversation=self.conversation,
        )
        self.assertEqual(result["content"], "app.js:1:function proposed() {}")

    def test_read_numbers_lines_of_the_pending_proposal(self):
        result = read_webapp_file(self.webapp, "app.js", conversation=self.conversation)
        self.assertEqual(result["content"], "     1\tfunction proposed() {}")
        self.assertEqual(result["total_lines"], 1)
