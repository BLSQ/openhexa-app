from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappModelTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.user_admin = User.objects.create_user(
            "admin@bluesquarehub.com",
            "admin",
        )
        WorkspaceMembership.objects.create(
            user=self.user_admin,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )
        self.user_viewer = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "foopassword",
        )
        WorkspaceMembership.objects.create(
            user=self.user_viewer,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.VIEWER,
        )
        self.user_editor = User.objects.create_user(
            "editor@bluesquarehub.com",
            "foopassword",
        )
        WorkspaceMembership.objects.create(
            user=self.user_editor,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.EDITOR,
        )
        self.webapp = Webapp.objects.create(
            name="Test Webapp",
            description="A test webapp",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )

    def test_webapp_creation(self):
        self.assertEqual(self.webapp.name, "Test Webapp")
        self.assertEqual(self.webapp.description, "A test webapp")
        self.assertEqual(self.webapp.workspace, self.workspace)
        self.assertEqual(self.webapp.created_by, self.user_admin)
        self.assertEqual(self.webapp.url, "https://example.com")

    def test_webapp_str(self):
        self.assertEqual(str(self.webapp), "Test Webapp")

    def test_webapp_update(self):
        self.webapp.name = "Updated Webapp"
        self.webapp.save()
        self.assertEqual(self.webapp.name, "Updated Webapp")

    def test_webapp_delete(self):
        webapp_id = self.webapp.id
        self.webapp.delete()
        with self.assertRaises(Webapp.DoesNotExist):
            Webapp.objects.get(id=webapp_id)
