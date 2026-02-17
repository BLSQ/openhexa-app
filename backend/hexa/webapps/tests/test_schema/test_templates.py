from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappsTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
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
        cls.WEBAPP = Webapp.objects.create(
            name="Test Webapp",
            slug="test-webapp",
            url="http://example.com",
            workspace=cls.WS1,
            created_by=cls.USER_ROOT,
        )

    def test_webapps_query(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            query webapps($workspaceSlug: String, $page: Int, $perPage: Int) {
                webapps(workspaceSlug: $workspaceSlug, page: $page, perPage: $perPage) {
                    items {
                        id
                        name
                        url
                        isFavorite
                        permissions {
                            update
                            delete
                        }
                    }
                    pageNumber
                    totalPages
                    totalItems
                }
            }
            """,
            {"workspaceSlug": self.WS1.slug, "page": 1, "perPage": 10},
        )
        self.assertEqual(1, len(response["data"]["webapps"]["items"]))
        webapp = response["data"]["webapps"]["items"][0]
        self.assertEqual(str(self.WEBAPP.id), webapp["id"])
        self.assertEqual("Test Webapp", webapp["name"])
        self.assertEqual("http://example.com", webapp["url"])
        self.assertFalse(webapp["isFavorite"])
        self.assertTrue(webapp["permissions"]["update"])
        self.assertTrue(webapp["permissions"]["delete"])

    def test_create_webapp(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation createWebapp($input: CreateWebappInput!) {
                createWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        id
                        name
                    }
                }
            }
            """,
            {
                "input": {
                    "name": "Test Webapp",
                    "workspaceSlug": self.WS1.slug,
                    "source": {"iframe": {"url": "http://newwebapp.com"}},
                }
            },
        )
        self.assertFalse(response["data"]["createWebapp"]["success"])
        self.assertEqual(response["data"]["createWebapp"]["errors"], ["ALREADY_EXISTS"])

        response = self.run_query(
            """
            mutation createWebapp($input: CreateWebappInput!) {
                createWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        id
                        name
                    }
                }
            }
            """,
            {
                "input": {
                    "name": "New Webapp",
                    "workspaceSlug": self.WS1.slug,
                    "source": {"iframe": {"url": "http://newwebapp.com"}},
                }
            },
        )
        self.assertTrue(response["data"]["createWebapp"]["success"])
        self.assertEqual(
            response["data"]["createWebapp"]["webapp"]["name"], "New Webapp"
        )

    def test_update_webapp(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation updateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        id
                        name
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.WEBAPP.id),
                    "name": "Updated Webapp",
                    "source": {"iframe": {"url": "http://updatedwebapp.com"}},
                }
            },
        )
        self.assertTrue(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            "Updated Webapp", response["data"]["updateWebapp"]["webapp"]["name"]
        )

    def test_delete_webapp(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation deleteWebapp($input: DeleteWebappInput!) {
                deleteWebapp(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"id": str(self.WEBAPP.id)}},
        )
        self.assertTrue(response["data"]["deleteWebapp"]["success"])
        self.assertFalse(Webapp.objects.filter(id=self.WEBAPP.id).exists())
        self.assertTrue(Webapp.all_objects.get(id=self.WEBAPP.id).is_deleted)

    def test_favorites(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation addToFavorites($input: AddToFavoritesInput!) {
                addToFavorites(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"webappId": str(self.WEBAPP.id)}},
        )
        self.assertTrue(response["data"]["addToFavorites"]["success"])
        self.assertTrue(
            self.USER_ROOT.favorite_webapps.filter(id=self.WEBAPP.id).exists()
        )

        response = self.run_query(
            """
            mutation removeFromFavorites($input: RemoveFromFavoritesInput!) {
                removeFromFavorites(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"webappId": str(self.WEBAPP.id)}},
        )
        self.assertTrue(response["data"]["removeFromFavorites"]["success"])
        self.assertFalse(
            self.USER_ROOT.favorite_webapps.filter(id=self.WEBAPP.id).exists()
        )
