from django.core.exceptions import ObjectDoesNotExist

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WorkspaceTest(TestCase):
    USER_SERENA = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com",
            "serena's password",
        )

    def test_create_workspace(self):
        self.assertEqual(0, Workspace.objects.all().count())
        workspace = Workspace(
            name="Senegal Workspace", description="This is test for creating workspace"
        )
        workspace.save()
        self.assertEqual(1, Workspace.objects.all().count())

    def test_get_workspace_by_id(self):
        workspace = Workspace(
            name="Senegal Workspace", description="This is test for creating workspace"
        )
        workspace.save()
        self.assertEqual(workspace, Workspace.objects.get(id=workspace.id))

    def test_get_workspace_by_id_failed(self):
        with self.assertRaises(ObjectDoesNotExist):
            Workspace.objects.get(pk="7bf4c750-f74b-4ed6-b7f7-b23e4cac4e2c")

    def test_add_member(self):
        workspace = Workspace(
            name="Senegal Workspace", description="This is test for creating workspace"
        )
        workspace.save()
        workspace_member_ship = WorkspaceMembership.objects.create(
            workspace=workspace,
            user=self.USER_SERENA,
            role=WorkspaceMembershipRole.ADMIN,
        )
        workspace_member_ship.save()
        self.assertEqual(
            workspace_member_ship,
            WorkspaceMembership.objects.get(id=workspace_member_ship.id),
        )
        self.assertEqual(self.USER_SERENA, workspace_member_ship.user)
        self.assertEqual(WorkspaceMembershipRole.ADMIN, workspace_member_ship.role)
