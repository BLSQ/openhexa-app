from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


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
