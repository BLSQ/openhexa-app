import shutil
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from hexa.files.backends.base import StorageObject
from hexa.files.backends.exceptions import NotFound
from hexa.files.backends.fs import FileSystemStorage
from hexa.mcp.tools.files import (
    glob_files,
    grep_files,
    list_files,
    read_file,
    write_file,
)

from .testutils import MCPTestCase


class ListFilesTest(MCPTestCase):
    @patch("hexa.files.schema.types.storage")
    def test_list_files(self, mock_storage):
        mock_storage.list_bucket_objects.return_value = {
            "items": [
                StorageObject(
                    key="test.csv",
                    name="test.csv",
                    path="test.csv",
                    size=1024,
                    updated_at=None,
                    type="file",
                ),
            ],
            "has_next_page": False,
            "has_previous_page": False,
            "page_number": 1,
        }
        result = list_files(user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["name"], "test.csv")
        self.assertEqual(result["items"][0]["type"], "FILE")
        self.assertEqual(result["items"][0]["size"], 1024)

    def test_list_files_workspace_not_found(self):
        result = list_files(user=self.USER_ADMIN, workspace_slug="nonexistent")
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_list_files_no_access(self):
        result = list_files(user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug)
        self.assertEqual(result, {"error": "Workspace not found"})


class ReadFileTest(MCPTestCase):
    @patch("hexa.files.schema.queries.storage")
    def test_read_file(self, mock_storage):
        mock_storage.read_object.return_value = b"col1,col2\nval1,val2"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="data.csv",
            name="data.csv",
            path="data.csv",
            size=19,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="data.csv",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "col1,col2\nval1,val2")

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_with_line_range(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\nline4\nline5\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="data.txt",
            name="data.txt",
            path="data.txt",
            size=30,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="data.txt",
            start_line=2,
            end_line=4,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "line2\nline3\nline4\n")

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_start_line_only(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="data.txt",
            name="data.txt",
            path="data.txt",
            size=18,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="data.txt",
            start_line=2,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "line2\nline3\n")

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_end_line_only(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="data.txt",
            name="data.txt",
            path="data.txt",
            size=18,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="data.txt",
            end_line=2,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "line1\nline2\n")


class WriteFileTest(MCPTestCase):
    @patch("hexa.files.schema.mutations.storage")
    def test_write_file(self, mock_storage):
        mock_storage.get_bucket_object.side_effect = NotFound("not found")
        mock_storage.save_object.return_value = None
        result = write_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="new-file.txt",
            content="hello world",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["filePath"], "new-file.txt")

    def test_write_file_no_access(self):
        result = write_file(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            file_path="new-file.txt",
            content="hello",
        )
        self.assertFalse(result["success"])


class _BucketTestCase(MCPTestCase):
    def setUp(self):
        self.data_directory = Path(mkdtemp())
        storage = FileSystemStorage(data_dir=self.data_directory)
        storage.create_bucket(self.WORKSPACE.bucket_name)
        for key, content in {
            "scripts/clean.py": b"import pandas\ndef clean(df):\n    return df\n",
            "scripts/load.py": b"def load():\n    pass\n",
            "data/raw.csv": b"a,b\n",
        }.items():
            storage.save_object(self.WORKSPACE.bucket_name, key, BytesIO(content))
        patcher = patch("hexa.mcp.tools.files.storage", storage)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        shutil.rmtree(self.data_directory)


class GlobFilesTest(_BucketTestCase):
    def test_glob_files_at_any_depth(self):
        result = glob_files(
            user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug, pattern="**/*.py"
        )
        self.assertEqual(
            result,
            {"paths": ["scripts/clean.py", "scripts/load.py"], "truncated": False},
        )

    def test_glob_files_under_prefix(self):
        result = glob_files(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pattern="**",
            prefix="data/",
        )
        self.assertEqual(result["paths"], ["data/raw.csv"])

    def test_glob_files_no_access(self):
        result = glob_files(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug, pattern="**"
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_glob_files_unsafe_prefix(self):
        result = glob_files(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pattern="**",
            prefix="../",
        )
        self.assertEqual(result, {"error": "Invalid prefix"})


class GrepFilesTest(_BucketTestCase):
    def test_grep_files_content(self):
        result = grep_files(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pattern=r"^def ",
            glob="**/*.py",
            output_mode="content",
        )
        self.assertEqual(
            result["content"],
            "scripts/clean.py:2:def clean(df):\nscripts/load.py:1:def load():",
        )

    def test_grep_files_only_reads_files_matching_glob(self):
        with patch.object(FileSystemStorage, "read_object", autospec=True) as read:
            read.return_value = b"def load():"
            grep_files(
                user=self.USER_ADMIN,
                workspace_slug=self.WORKSPACE.slug,
                pattern="def",
                glob="scripts/load.py",
            )
        read.assert_called_once()

    @patch("hexa.mcp.tools.files.GREP_MAX_DOWNLOAD_BYTES", 1)
    def test_grep_files_stops_at_the_download_budget(self):
        result = grep_files(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pattern="def",
            glob="**/*.py",
            output_mode="count",
        )
        self.assertEqual(result["counts"], {"scripts/clean.py": 1})
        self.assertTrue(result["truncated"])
        self.assertIn("stopped after 1 of 2 files", result["notice"])

    @patch("hexa.mcp.tools.files.GREP_TIMEOUT_SECONDS", 0)
    def test_grep_files_stops_at_the_timeout(self):
        result = grep_files(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pattern="def",
            glob="**/*.py",
        )
        self.assertEqual(result["files"], [])
        self.assertIn("stopped after 0 of 2 files", result["notice"])

    @patch("hexa.files.bucket_file_source.MAX_LISTED_FILES", 2)
    @patch("hexa.mcp.tools.files.GREP_MAX_DOWNLOAD_BYTES", 1)
    def test_grep_files_keeps_both_notices(self):
        result = grep_files(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pattern="a",
            glob="**",
        )
        self.assertIn("Search stopped", result["notice"])
        self.assertIn("Only the first", result["notice"])

    def test_grep_files_no_access(self):
        result = grep_files(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            pattern="def",
            glob="**",
        )
        self.assertEqual(result, {"error": "Workspace not found"})


class ReadFileWithLineNumbersTest(MCPTestCase):
    @patch("hexa.files.schema.queries.storage")
    def test_read_file_with_line_numbers(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="data.txt",
            name="data.txt",
            path="data.txt",
            size=18,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="data.txt",
            start_line=2,
            line_numbers=True,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "     2\tline2\n     3\tline3")
        self.assertEqual(result["total_lines"], 3)
