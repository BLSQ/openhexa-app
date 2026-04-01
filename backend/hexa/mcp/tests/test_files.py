from unittest.mock import patch

from hexa.files.backends.base import StorageObject
from hexa.files.backends.exceptions import NotFound
from hexa.mcp.tools.files import list_files, read_file, write_file

from .testutils import MCPTestCase


class ListFilesTest(MCPTestCase):
    @patch("hexa.files.schema.queries.storage")
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
        self.assertEqual(result["items"][0]["type"], "file")
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
