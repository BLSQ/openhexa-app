from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.files.backends.base import StorageObject
from hexa.files.backends.exceptions import NotFound
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class FilesTest(GraphQLTestCase):
    USER_WORKSPACE_ADMIN = None
    WORKSPACE = None
    FOLDER_NAME = "/new_folder"

    @classmethod
    def setUpTestData(cls):
        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "workspaceroot@bluesquarehub.com", "workspace", is_superuser=True
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_WORKSPACE_ADMIN,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.USER_WORKSPACE_ADMIN,
            name="Burundi Workspace",
            description="This is a workspace for Burundi",
            countries=[{"code": "AD"}],
        )

        cls.USER_VIEWER = User.objects.create_user("viewer@bluesquarehub.com", "viewer")
        WorkspaceMembership.objects.create(
            user=cls.USER_VIEWER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_workspace_objects_authorized(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)

        r = self.run_query(
            """
        query WorkspaceObjects ($workspaceSlug: String!) {
            workspace (slug: $workspaceSlug) {
                bucket {
                    objects(prefix: "start/") {
                        hasNextPage
                        hasPreviousPage
                        items {
                            name
                        }
                    }
                }
            }
        }
        """,
            {"workspaceSlug": self.WORKSPACE.slug},
        )
        self.assertEqual(
            {
                "bucket": {
                    "objects": {
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                        "items": [],
                    }
                }
            },
            r["data"]["workspace"],
        )

    @patch("hexa.files.schema.mutations.storage")
    def test_create_bucket_folder(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        mock_storage.create_bucket_folder.return_value = {"name": self.FOLDER_NAME}

        r = self.run_query(
            """
        mutation CreateBucketFolder($input: CreateBucketFolderInput!) {
            createBucketFolder(input: $input) {
                success
                errors
                folder {
                    name
                }
            }
        }
        """,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "folderKey": self.FOLDER_NAME,
                }
            },
        )
        self.assertEqual(
            {"success": True, "errors": [], "folder": {"name": self.FOLDER_NAME}},
            r["data"]["createBucketFolder"],
        )
        mock_storage.create_bucket_folder.assert_called_once_with(
            self.WORKSPACE.bucket_name, self.FOLDER_NAME
        )

    @patch("hexa.files.schema.queries.storage")
    def test_get_file_by_path(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)

        file_path = "test/file.txt"
        mock_file = StorageObject(
            key="file.txt",
            name="file.txt",
            path=file_path,
            size=1024,
            updated_at=None,
            type="file",
        )
        mock_storage.get_bucket_object.return_value = mock_file

        r = self.run_query(
            """
            query GetFileByPath($workspaceSlug: String!, $path: String!) {
                getFileByPath(workspaceSlug: $workspaceSlug, path: $path) {
                    key
                    name
                    path
                    size
                    type
                }
            }
            """,
            {"workspaceSlug": self.WORKSPACE.slug, "path": file_path},
        )

        self.assertEqual(
            {
                "key": "file.txt",
                "name": "file.txt",
                "path": file_path,
                "size": 1024,
                "type": "FILE",  # converted to uppercase by the type resolver
            },
            r["data"]["getFileByPath"],
        )
        mock_storage.get_bucket_object.assert_called_once_with(
            self.WORKSPACE.bucket_name, file_path
        )

    @patch("hexa.files.schema.queries.storage")
    def test_get_file_by_path_file_not_found(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)

        # Mock file not found by importing the correct exception
        from hexa.files.backends.exceptions import NotFound

        mock_storage.get_bucket_object.side_effect = NotFound("File not found")

        r = self.run_query(
            """
            query GetFileByPath($workspaceSlug: String!, $path: String!) {
                getFileByPath(workspaceSlug: $workspaceSlug, path: $path) {
                    key
                }
            }
            """,
            {"workspaceSlug": self.WORKSPACE.slug, "path": "nonexistent/file.txt"},
        )

        self.assertIsNone(r["data"]["getFileByPath"])

    def test_get_file_by_path_workspace_not_found(self):
        non_workspace_member = User.objects.create_user("regular@blsq.org", "password")
        self.client.force_login(non_workspace_member)

        r = self.run_query(
            """
            query GetFileByPath($workspaceSlug: String!, $path: String!) {
                getFileByPath(workspaceSlug: $workspaceSlug, path: $path) {
                    key
                }
            }
            """,
            {"workspaceSlug": self.WORKSPACE.slug, "path": "test/file.txt"},
        )

        self.assertIsNone(r["data"]["getFileByPath"])

    READ_FILE_CONTENT_QUERY = """
        query ReadFileContent($workspaceSlug: String!, $filePath: String!) {
            readFileContent(workspaceSlug: $workspaceSlug, filePath: $filePath) {
                success
                errors
                content
                size
            }
        }
    """

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_content(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="file.txt", name="file.txt", path="file.txt", size=100, type="file"
        )
        mock_storage.read_object.return_value = b"hello world"

        r = self.run_query(
            self.READ_FILE_CONTENT_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug, "filePath": "file.txt"},
        )
        result = r["data"]["readFileContent"]
        self.assertTrue(result["success"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["content"], "hello world")
        self.assertEqual(result["size"], 11)

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_content_not_found(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        mock_storage.get_bucket_object.side_effect = NotFound("not found")

        r = self.run_query(
            self.READ_FILE_CONTENT_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug, "filePath": "missing.txt"},
        )
        result = r["data"]["readFileContent"]
        self.assertFalse(result["success"])
        self.assertIn("NOT_FOUND", result["errors"])

    def test_read_file_content_not_a_member(self):
        non_member = User.objects.create_user("outsider@blsq.org", "password")
        self.client.force_login(non_member)

        r = self.run_query(
            self.READ_FILE_CONTENT_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug, "filePath": "file.txt"},
        )
        result = r["data"]["readFileContent"]
        self.assertFalse(result["success"])
        self.assertIn("NOT_FOUND", result["errors"])

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_content_too_large(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="big.bin",
            name="big.bin",
            path="big.bin",
            size=2 * 1024 * 1024,
            type="file",
        )

        r = self.run_query(
            self.READ_FILE_CONTENT_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug, "filePath": "big.bin"},
        )
        result = r["data"]["readFileContent"]
        self.assertFalse(result["success"])
        self.assertIn("FILE_TOO_LARGE", result["errors"])

    @patch("hexa.files.schema.queries.storage")
    def test_read_file_content_not_a_file(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="somedir/", name="somedir", path="somedir/", size=0, type="directory"
        )

        r = self.run_query(
            self.READ_FILE_CONTENT_QUERY,
            {"workspaceSlug": self.WORKSPACE.slug, "filePath": "somedir/"},
        )
        result = r["data"]["readFileContent"]
        self.assertFalse(result["success"])
        self.assertIn("NOT_A_FILE", result["errors"])

    WRITE_FILE_CONTENT_MUTATION = """
        mutation WriteFileContent($input: WriteFileContentInput!) {
            writeFileContent(input: $input) {
                success
                errors
                filePath
                size
            }
        }
    """

    @patch("hexa.files.schema.mutations.storage")
    def test_write_file_content(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        # overwrite defaults to False, so the resolver checks if the file exists first.
        # Raise NotFound to simulate a new file that doesn't exist yet.
        mock_storage.get_bucket_object.side_effect = NotFound("not found")

        r = self.run_query(
            self.WRITE_FILE_CONTENT_MUTATION,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "filePath": "new_file.txt",
                    "content": "hello",
                }
            },
        )
        result = r["data"]["writeFileContent"]
        self.assertTrue(result["success"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["filePath"], "new_file.txt")
        self.assertEqual(result["size"], 5)
        mock_storage.save_object.assert_called_once()

    @patch("hexa.files.schema.mutations.storage")
    def test_write_file_content_overwrite_blocked(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="existing.txt",
            name="existing.txt",
            path="existing.txt",
            size=10,
            type="file",
        )

        r = self.run_query(
            self.WRITE_FILE_CONTENT_MUTATION,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "filePath": "existing.txt",
                    "content": "new content",
                    "overwrite": False,
                }
            },
        )
        result = r["data"]["writeFileContent"]
        self.assertFalse(result["success"])
        self.assertIn("ALREADY_EXISTS", result["errors"])
        mock_storage.save_object.assert_not_called()

    @patch("hexa.files.schema.mutations.storage")
    def test_write_file_content_overwrite_allowed(self, mock_storage):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="existing.txt",
            name="existing.txt",
            path="existing.txt",
            size=10,
            type="file",
        )

        r = self.run_query(
            self.WRITE_FILE_CONTENT_MUTATION,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "filePath": "existing.txt",
                    "content": "overwritten",
                    "overwrite": True,
                }
            },
        )
        result = r["data"]["writeFileContent"]
        self.assertTrue(result["success"])
        self.assertEqual(result["errors"], [])
        mock_storage.save_object.assert_called_once()

    def test_write_file_content_permission_denied(self):
        self.client.force_login(self.USER_VIEWER)

        r = self.run_query(
            self.WRITE_FILE_CONTENT_MUTATION,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "filePath": "file.txt",
                    "content": "hello",
                }
            },
        )
        result = r["data"]["writeFileContent"]
        self.assertFalse(result["success"])
        self.assertIn("PERMISSION_DENIED", result["errors"])

    def test_write_file_content_workspace_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)

        r = self.run_query(
            self.WRITE_FILE_CONTENT_MUTATION,
            {
                "input": {
                    "workspaceSlug": "nonexistent-workspace",
                    "filePath": "file.txt",
                    "content": "hello",
                }
            },
        )
        result = r["data"]["writeFileContent"]
        self.assertFalse(result["success"])
        self.assertIn("NOT_FOUND", result["errors"])
