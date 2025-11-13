from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from hexa.shortcuts.models import Shortcut
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Workspace, WorkspaceMembership


class ShortcutModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@openhexa.org",
            password="password",
        )
        cls.workspace = Workspace.objects.create(name="Test Workspace")
        WorkspaceMembership.objects.create(
            workspace=cls.workspace,
            user=cls.user,
        )
        cls.webapp = Webapp.objects.create(
            name="Test Webapp",
            url="https://example.com",
            workspace=cls.workspace,
            created_by=cls.user,
        )

    def test_create_shortcut(self):
        content_type = ContentType.objects.get_for_model(Webapp)
        shortcut = Shortcut.objects.create(
            user=self.user,
            workspace=self.workspace,
            content_type=content_type,
            object_id=self.webapp.id,
        )

        self.assertEqual(shortcut.user, self.user)
        self.assertEqual(shortcut.workspace, self.workspace)
        self.assertEqual(shortcut.content_object, self.webapp)

    def test_filter_for_user(self):
        content_type = ContentType.objects.get_for_model(Webapp)
        Shortcut.objects.create(
            user=self.user,
            workspace=self.workspace,
            content_type=content_type,
            object_id=self.webapp.id,
        )

        shortcuts = Shortcut.objects.filter_for_user(self.user)
        self.assertEqual(shortcuts.count(), 1)
        self.assertEqual(shortcuts.first().content_object, self.webapp)

    def test_filter_for_workspace(self):
        content_type = ContentType.objects.get_for_model(Webapp)
        Shortcut.objects.create(
            user=self.user,
            workspace=self.workspace,
            content_type=content_type,
            object_id=self.webapp.id,
        )

        shortcuts = Shortcut.objects.filter_for_workspace(self.workspace)
        self.assertEqual(shortcuts.count(), 1)

    def test_filter_by_content_type(self):
        content_type = ContentType.objects.get_for_model(Webapp)
        Shortcut.objects.create(
            user=self.user,
            workspace=self.workspace,
            content_type=content_type,
            object_id=self.webapp.id,
        )

        shortcuts = Shortcut.objects.filter_by_content_type(Webapp)
        self.assertEqual(shortcuts.count(), 1)

    def test_unique_constraint(self):
        content_type = ContentType.objects.get_for_model(Webapp)

        Shortcut.objects.create(
            user=self.user,
            workspace=self.workspace,
            content_type=content_type,
            object_id=self.webapp.id,
        )

        with self.assertRaises(Exception):
            Shortcut.objects.create(
                user=self.user,
                workspace=self.workspace,
                content_type=content_type,
                object_id=self.webapp.id,
            )

    def test_webapp_helper_methods(self):
        self.assertFalse(self.webapp.is_shortcut(self.user))

        self.webapp.add_to_shortcuts(self.user)
        self.assertTrue(self.webapp.is_shortcut(self.user))

        self.webapp.remove_from_shortcuts(self.user)
        self.assertFalse(self.webapp.is_shortcut(self.user))
