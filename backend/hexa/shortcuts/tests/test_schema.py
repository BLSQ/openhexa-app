from hexa.core.test import GraphQLTestCase
from hexa.shortcuts.models import Shortcut
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ShortcutsSchemaTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.USER_REGULAR = User.objects.create_user(
            "user@bluesquarehub.com",
            "standardpassword",
        )
        cls.WS1 = Workspace.objects.create(
            name="WS1",
            description="Workspace 1",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_ROOT,
            workspace=cls.WS1,
            role=WorkspaceMembershipRole.ADMIN,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_REGULAR,
            workspace=cls.WS1,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.WEBAPP1 = Webapp.objects.create(
            name="Test Webapp 1",
            url="http://example1.com",
            workspace=cls.WS1,
            created_by=cls.USER_ROOT,
        )
        cls.WEBAPP2 = Webapp.objects.create(
            name="Test Webapp 2",
            url="http://example2.com",
            workspace=cls.WS1,
            created_by=cls.USER_ROOT,
        )

    def test_shortcuts_query_empty(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            query shortcuts($workspaceSlug: String!) {
                shortcuts(workspaceSlug: $workspaceSlug) {
                    id
                    name
                    url
                    type
                    order
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug},
        )
        self.assertEqual(0, len(response["data"]["shortcuts"]))

    def test_shortcuts_query_with_shortcuts(self):
        self.WEBAPP1.add_to_shortcuts(self.USER_ROOT)
        self.WEBAPP2.add_to_shortcuts(self.USER_ROOT)

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            query shortcuts($workspaceSlug: String!) {
                shortcuts(workspaceSlug: $workspaceSlug) {
                    id
                    name
                    url
                    type
                    order
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug},
        )

        shortcuts = response["data"]["shortcuts"]
        self.assertEqual(2, len(shortcuts))
        self.assertEqual("Test Webapp 1", shortcuts[0]["name"])
        self.assertEqual("Test Webapp 2", shortcuts[1]["name"])
        self.assertEqual("webapp", shortcuts[0]["type"])

    def test_shortcuts_query_user_specific(self):
        self.WEBAPP1.add_to_shortcuts(self.USER_ROOT)

        self.client.force_login(self.USER_REGULAR)
        response = self.run_query(
            """
            query shortcuts($workspaceSlug: String!) {
                shortcuts(workspaceSlug: $workspaceSlug) {
                    id
                    name
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug},
        )

        self.assertEqual(0, len(response["data"]["shortcuts"]))

    def test_add_to_shortcuts_mutation(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation addToShortcuts($input: AddToShortcutsInput!) {
                addToShortcuts(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"webappId": str(self.WEBAPP1.id)}},
        )

        self.assertTrue(response["data"]["addToShortcuts"]["success"])
        self.assertEqual([], response["data"]["addToShortcuts"]["errors"])
        self.assertTrue(self.WEBAPP1.is_shortcut(self.USER_ROOT))

    def test_add_to_shortcuts_mutation_webapp_not_found(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation addToShortcuts($input: AddToShortcutsInput!) {
                addToShortcuts(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"webappId": "00000000-0000-0000-0000-000000000000"}},
        )

        self.assertFalse(response["data"]["addToShortcuts"]["success"])
        self.assertIn("ITEM_NOT_FOUND", response["data"]["addToShortcuts"]["errors"])

    def test_remove_from_shortcuts_mutation(self):
        self.WEBAPP1.add_to_shortcuts(self.USER_ROOT)
        self.assertTrue(self.WEBAPP1.is_shortcut(self.USER_ROOT))

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation removeFromShortcuts($input: RemoveFromShortcutsInput!) {
                removeFromShortcuts(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"webappId": str(self.WEBAPP1.id)}},
        )

        self.assertTrue(response["data"]["removeFromShortcuts"]["success"])
        self.assertEqual([], response["data"]["removeFromShortcuts"]["errors"])
        self.assertFalse(self.WEBAPP1.is_shortcut(self.USER_ROOT))

    def test_webapp_is_shortcut_field(self):
        self.WEBAPP1.add_to_shortcuts(self.USER_ROOT)

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            query webapps($workspaceSlug: String!) {
                webapps(workspaceSlug: $workspaceSlug) {
                    items {
                        id
                        name
                        isShortcut
                    }
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug},
        )

        webapps = response["data"]["webapps"]["items"]
        webapp1 = next(w for w in webapps if w["id"] == str(self.WEBAPP1.id))
        webapp2 = next(w for w in webapps if w["id"] == str(self.WEBAPP2.id))

        self.assertTrue(webapp1["isShortcut"])
        self.assertFalse(webapp2["isShortcut"])

    def test_shortcuts_skip_deleted_webapps(self):
        self.WEBAPP1.add_to_shortcuts(self.USER_ROOT)
        shortcut_count = Shortcut.objects.filter(user=self.USER_ROOT).count()
        self.assertEqual(1, shortcut_count)

        self.WEBAPP1.delete()

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            query shortcuts($workspaceSlug: String!) {
                shortcuts(workspaceSlug: $workspaceSlug) {
                    id
                    name
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug},
        )

        self.assertEqual(0, len(response["data"]["shortcuts"]))
