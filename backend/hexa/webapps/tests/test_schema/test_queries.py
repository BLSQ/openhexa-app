from django.utils import timezone

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappQueriesTest(GraphQLTestCase):
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

    def test_public_webapp_query_without_auth_succeeds(self):
        """Unauthenticated users can query public webapps"""
        webapp = Webapp.objects.create(
            name="Public Test",
            slug="public-test",
            type=Webapp.WebappType.HTML,
            content="<html><body>Public</body></html>",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
            is_public=True,
        )

        response = self.run_query(
            """
            query publicWebapp($workspaceSlug: String!, $slug: String!) {
                publicWebapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                    id
                    name
                    isPublic
                    type
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug, "slug": webapp.slug},
        )

        self.assertEqual(response["data"]["publicWebapp"]["name"], "Public Test")
        self.assertEqual(response["data"]["publicWebapp"]["isPublic"], True)
        self.assertEqual(response["data"]["publicWebapp"]["type"], "HTML")

    def test_public_webapp_query_for_private_webapp_returns_none(self):
        """Unauthenticated users cannot query private webapps"""
        webapp = Webapp.objects.create(
            name="Private Test",
            slug="private-test",
            type=Webapp.WebappType.HTML,
            content="<html><body>Private</body></html>",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
            is_public=False,
        )

        response = self.run_query(
            """
            query publicWebapp($workspaceSlug: String!, $slug: String!) {
                publicWebapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                    id
                    name
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug, "slug": webapp.slug},
        )

        self.assertIsNone(response["data"]["publicWebapp"])

    def test_public_webapp_query_for_archived_workspace_returns_none(self):
        """Public webapps in archived workspaces are not accessible"""
        self.WS1.archived = True
        self.WS1.save()

        webapp = Webapp.objects.create(
            name="Public in Archived",
            slug="public-archived",
            type=Webapp.WebappType.HTML,
            content="<html><body>Archived</body></html>",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
            is_public=True,
        )

        response = self.run_query(
            """
            query publicWebapp($workspaceSlug: String!, $slug: String!) {
                publicWebapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                    id
                    name
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug, "slug": webapp.slug},
        )

        self.assertIsNone(response["data"]["publicWebapp"])

    def test_public_webapp_query_for_deleted_webapp_returns_none(self):
        """Soft-deleted public webapps are not accessible"""
        webapp = Webapp.objects.create(
            name="Deleted Public",
            slug="deleted-public",
            type=Webapp.WebappType.HTML,
            content="<html><body>Deleted</body></html>",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
            is_public=True,
        )
        webapp.deleted_at = timezone.now()
        webapp.save()

        response = self.run_query(
            """
            query publicWebapp($workspaceSlug: String!, $slug: String!) {
                publicWebapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                    id
                    name
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug, "slug": webapp.slug},
        )

        self.assertIsNone(response["data"]["publicWebapp"])

    def test_public_webapp_query_for_nonexistent_workspace_returns_none(self):
        """Query with non-existent workspace returns None"""
        response = self.run_query(
            """
            query publicWebapp($workspaceSlug: String!, $slug: String!) {
                publicWebapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                    id
                    name
                }
            }
            """,
            {"workspaceSlug": "non-existent", "slug": "test"},
        )

        self.assertIsNone(response["data"]["publicWebapp"])

    def test_authenticated_user_can_query_public_webapp(self):
        """Authenticated users can also query public webapps"""
        self.client.force_login(self.USER_REGULAR)

        webapp = Webapp.objects.create(
            name="Public Test",
            slug="public-test-auth",
            type=Webapp.WebappType.HTML,
            content="<html><body>Public</body></html>",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
            is_public=True,
        )

        response = self.run_query(
            """
            query publicWebapp($workspaceSlug: String!, $slug: String!) {
                publicWebapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                    id
                    name
                    isPublic
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug, "slug": webapp.slug},
        )

        self.assertEqual(response["data"]["publicWebapp"]["name"], "Public Test")
        self.assertEqual(response["data"]["publicWebapp"]["isPublic"], True)
