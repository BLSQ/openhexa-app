from hexa.user_management.models import Organization, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


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

        cls.ORGANIZATION = Organization.objects.create(
            name="Data Studio Organization", organization_type="CORPORATE"
        )
        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="My Workspace",
            description="Test workspace",
            organization=cls.ORGANIZATION,
        )
        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="My Workspace 2",
            description="Test workspace 2",
            organization=cls.ORGANIZATION,
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
