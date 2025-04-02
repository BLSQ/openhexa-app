from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

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

    def test_webapp_soft_delete(self):
        webapp_id = self.webapp.id
        self.webapp.delete()
        self.assertFalse(Webapp.objects.filter(id=webapp_id).exists())
        self.assertTrue(Webapp.all_objects.get(id=webapp_id).is_deleted)

    def test_is_favorite(self):
        self.assertFalse(self.webapp.is_favorite(self.user_viewer))
        self.webapp.add_to_favorites(self.user_viewer)
        self.assertTrue(self.webapp.is_favorite(self.user_viewer))

    def test_add_to_favorites(self):
        self.webapp.add_to_favorites(self.user_viewer)
        self.assertIn(self.user_viewer, self.webapp.favorites.all())

    def test_remove_from_favorites(self):
        self.webapp.add_to_favorites(self.user_viewer)
        self.webapp.remove_from_favorites(self.user_viewer)
        self.assertNotIn(self.user_viewer, self.webapp.favorites.all())

    def test_create_if_has_perm(self):
        with self.assertRaises(PermissionDenied):
            Webapp.objects.create_if_has_perm(
                self.user_viewer,
                self.workspace,
                name="New Webapp",
                workspace=self.workspace,
                created_by=self.user_viewer,
                url="https://example.com",
            )

        webapp = Webapp.objects.create_if_has_perm(
            self.user_admin,
            self.workspace,
            name="New Webapp1",
            workspace=self.workspace,
            created_by=self.user_admin,
            url="https://example.com",
        )
        self.assertTrue(Webapp.objects.filter(id=webapp.id).exists())

        webapp = Webapp.objects.create_if_has_perm(
            self.user_editor,
            self.workspace,
            name="New Webapp2",
            workspace=self.workspace,
            created_by=self.user_editor,
            url="https://example.com",
        )
        self.assertTrue(Webapp.objects.filter(id=webapp.id).exists())

    def test_update_if_has_perm(self):
        with self.assertRaises(PermissionDenied):
            Webapp.objects.update_if_has_perm(
                self.user_viewer, self.webapp, name="Updated Webapp"
            )

        webapp = Webapp.objects.update_if_has_perm(
            self.user_admin, self.webapp, name="Updated Webapp by admin"
        )
        self.assertEqual(webapp.name, "Updated Webapp by admin")

        webapp = Webapp.objects.update_if_has_perm(
            self.user_editor, self.webapp, name="Updated Webapp by editor"
        )
        self.assertEqual(webapp.name, "Updated Webapp by editor")

    def test_delete_if_has_perm(self):
        with self.assertRaises(PermissionDenied):
            Webapp.objects.delete_if_has_perm(self.user_viewer, self.webapp)

        with self.assertRaises(PermissionDenied):
            Webapp.objects.delete_if_has_perm(self.user_editor, self.webapp)

        Webapp.objects.delete_if_has_perm(self.user_admin, self.webapp)
        self.assertFalse(Webapp.objects.filter(id=self.webapp.id).exists())
        self.assertTrue(Webapp.all_objects.get(id=self.webapp.id).is_deleted)

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Webapp.objects.create(
                name=self.webapp.name,
                workspace=self.webapp.workspace,
                created_by=self.user_admin,
                url="https://example.com",
            )
