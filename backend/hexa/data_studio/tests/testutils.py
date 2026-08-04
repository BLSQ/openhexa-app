from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.user_management.models import User
from hexa.workspaces.models import (
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace


class SavedQueryTestMixin:
    """Shared fixtures for saved-query tests.

    - USER_ADMIN:  admin of WORKSPACE
    - USER_EDITOR: editor of WORKSPACE
    - USER_VIEWER: viewer of WORKSPACE
    - USER_OUTSIDER: no membership anywhere
    - WORKSPACE_2: a second workspace USER_ADMIN belongs to (isolation checks)
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "adminpassword", is_superuser=True
        )
        cls.USER_EDITOR = User.objects.create_user(
            "editor@bluesquarehub.com", "editorpassword"
        )
        cls.USER_VIEWER = User.objects.create_user(
            "viewer@bluesquarehub.com", "viewerpassword"
        )
        cls.USER_OUTSIDER = User.objects.create_user(
            "outsider@bluesquarehub.com", "outsiderpassword"
        )

        cls.WORKSPACE = create_workspace(
            cls.USER_ADMIN, name="My Workspace", description="Test workspace"
        )
        cls.WORKSPACE_2 = create_workspace(
            cls.USER_ADMIN, name="My Workspace 2", description="Test workspace 2"
        )

        cls.USER_ADMIN.is_superuser = False
        cls.USER_ADMIN.save()

        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def create_saved_query(
        self,
        user=None,
        workspace=None,
        name="My query",
        content="SELECT 1",
        description="a query",
        visibility=SavedQueryVisibility.WORKSPACE,
    ):
        """Create a saved query, workspace-shared unless stated otherwise.

        The model itself defaults to PRIVATE; tests about what one user can do to
        another user's query say which visibility they mean rather than leaning on
        that default, so flipping it later cannot silently reinterpret them.
        """
        return SavedQuery.objects.create_if_has_perm(
            user or self.USER_EDITOR,
            workspace or self.WORKSPACE,
            name=name,
            content=content,
            description=description,
            visibility=visibility,
        )
