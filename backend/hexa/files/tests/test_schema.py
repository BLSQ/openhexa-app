from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.files.backends.base import StorageObject
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
            updated=None,
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
