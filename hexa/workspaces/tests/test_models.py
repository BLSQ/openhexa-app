from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WorkspaceTest(TestCase):
    USER_SERENA = None
    USER_ADMIN = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )

        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "admin", is_superuser=True
        )

    def test_create_workspace_regular_user(self):
        with self.assertRaises(PermissionDenied):
            workspace = Workspace.objects.create_if_has_perm(
                self.USER_SERENA,
                name="Senegal Workspace",
                description="This is test for creating workspace",
            )
            workspace.save()

    def test_create_workspace_admin_user(self):
        workspace = Workspace.objects.create_if_has_perm(
            self.USER_ADMIN,
            name="Senegal Workspace",
            description="This is test for creating workspace",
        )
        workspace.save()
        self.assertEqual(1, Workspace.objects.all().count())

    def test_get_workspace_by_id(self):
        workspace = Workspace.objects.create_if_has_perm(
            self.USER_ADMIN,
            name="Senegal Workspace",
            description="This is test for creating workspace",
        )
        workspace.save()
        self.assertEqual(workspace, Workspace.objects.get(id=workspace.id))

    def test_get_workspace_by_id_failed(self):
        with self.assertRaises(ObjectDoesNotExist):
            Workspace.objects.get(pk="7bf4c750-f74b-4ed6-b7f7-b23e4cac4e2c")

    def test_add_member(self):
        workspace = Workspace.objects.create_if_has_perm(
            self.USER_ADMIN,
            name="Senegal Workspace",
            description="This is test for creating workspace",
        )
        workspace.save()
        self.assertTrue(
            WorkspaceMembership.objects.filter(
                user=self.USER_ADMIN,
                workspace=workspace,
                role=WorkspaceMembershipRole.ADMIN,
            ).exists()
        )
