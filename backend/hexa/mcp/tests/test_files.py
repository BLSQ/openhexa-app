import shutil
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from hexa.files.backends.base import StorageObject
from hexa.files.backends.exceptions import NotFound
from hexa.files.backends.fs import FileSystemStorage
from hexa.mcp.tools.files import (
    READABLE_EXTENSIONS,
    glob_files,
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
        mock_storage.read_object.return_value = b"import os\nprint(os.getcwd())"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="script.py",
            name="script.py",
            path="script.py",
            size=31,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="script.py",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "import os\nprint(os.getcwd())")

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_with_line_range(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\nline4\nline5\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="script.py",
            name="script.py",
            path="script.py",
            size=30,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="script.py",
            start_line=2,
            end_line=4,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "line2\nline3\nline4\n")

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_start_line_only(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="script.py",
            name="script.py",
            path="script.py",
            size=18,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="script.py",
            start_line=2,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "line2\nline3\n")

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_end_line_only(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="script.py",
            name="script.py",
            path="script.py",
            size=18,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="script.py",
            end_line=2,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "line1\nline2\n")

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_refuses_non_source_files(self, mock_storage):
        for file_path in [
            "data.csv",
            "config.json",
            "analysis.ipynb",
            "notes.txt",
            "DATA.CSV",
            "scripts/data.py.csv",
            ".env",
            "Dockerfile",
        ]:
            with self.subTest(file_path=file_path):
                result = read_file(
                    user=self.USER_ADMIN,
                    workspace_slug=self.WORKSPACE.slug,
                    file_path=file_path,
                )
                self.assertIn(
                    "only reads source code and documentation files", result["error"]
                )
        mock_storage.read_object.assert_not_called()
        mock_storage.get_bucket_object.assert_not_called()

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_extension_is_case_insensitive(self, mock_storage):
        mock_storage.read_object.return_value = b"x <- 1"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="analysis.R",
            name="analysis.R",
            path="analysis.R",
            size=6,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="analysis.R",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "x <- 1")

    def test_read_file_description_lists_every_readable_extension(self):
        for extension in READABLE_EXTENSIONS:
            with self.subTest(extension=extension):
                self.assertIn(extension, read_file.__doc__)


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
        patcher = patch("hexa.files.schema.queries.storage", storage)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        shutil.rmtree(self.data_directory)


class GlobFilesTest(_BucketTestCase):
    def test_glob_files_at_any_depth(self):
        result = glob_files(
            user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug, pattern="**/*.py"
        )
        self.assertEqual(result["paths"], ["scripts/clean.py", "scripts/load.py"])
        self.assertFalse(result["truncated"])

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
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["NOT_FOUND"])

    def test_glob_files_unsafe_prefix(self):
        result = glob_files(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            pattern="**",
            prefix="../",
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["INVALID_PATH"])


class ReadFileWithLineNumbersTest(MCPTestCase):
    @patch("hexa.files.schema.queries.storage")
    def test_read_file_with_line_numbers(self, mock_storage):
        mock_storage.read_object.return_value = b"line1\nline2\nline3\n"
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="script.py",
            name="script.py",
            path="script.py",
            size=18,
            updated_at=None,
            type="file",
        )
        result = read_file(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            file_path="script.py",
            start_line=2,
            line_numbers=True,
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "     2\tline2\n     3\tline3")
        self.assertEqual(result["totalLines"], 3)
