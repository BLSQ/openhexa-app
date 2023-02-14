from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.files.api import ObjectsPage
from hexa.user_management.models import Feature, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

from .mocks.mockgcp import create_storage_mock

storage = create_storage_mock()


class WorkspaceTest(GraphQLTestCase):
    USER_EDITOR = None
    USER_WORKSPACE_ADMIN = None
    WORKSPACE = None

    @classmethod
    def setUpTestData(cls):
        Feature.objects.create(code="workspaces", force_activate=True)

        cls.USER_EDITOR = User.objects.create_user(
            "editor@bluesquarehub.com",
            "standardpassword",
        )

        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "workspaceroot@bluesquarehub.com",
            "workspace",
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_EDITOR,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.USER_EDITOR,
            name="Burundi Workspace",
            description="This is a workspace for Burundi",
            countries=[{"code": "AD"}],
        )

        cls.WORKSPACE_MEMBERSHIP = WorkspaceMembership.objects.create(
            user=cls.USER_EDITOR,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.EDITOR,
        )

        cls.WORKSPACE_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            user=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    @patch("hexa.files.schema.types.list_bucket_objects")
    def test_workspace_objects_authorized(self, mock_list_object):
        mock_list_object.return_value = ObjectsPage(
            next_page_token="next_page", items=[{"name": "first-directory/"}]
        )

        self.client.force_login(self.USER_EDITOR)

        r = self.run_query(
            """
        query WorkspaceObjects ($workspaceSlug: String!) {
            workspace (slug: $workspaceSlug) {
                bucket {
                    objects(prefix: "start/") {
                        nextPageToken
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
                        "nextPageToken": "next_page",
                        "items": [{"name": "first-directory/"}],
                    }
                }
            },
            r["data"]["workspace"],
        )
        mock_list_object.assert_called_with(
            self.WORKSPACE, prefix="start/", page_token=None
        )
