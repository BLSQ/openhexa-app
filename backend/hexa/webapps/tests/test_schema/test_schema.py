from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappsTest(GraphQLTestCase):
    UPDATE_WEBAPP_SUBDOMAIN_MUTATION = """
        mutation updateWebapp($input: UpdateWebappInput!) {
            updateWebapp(input: $input) {
                success
                errors
                webapp {
                    id
                    subdomain
                }
            }
        }
    """

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

    def test_update_webapp_subdomain(self):
        self.client.force_login(self.USER_ROOT)

        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": "my-webapp"}},
        )
        self.assertTrue(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            "my-webapp", response["data"]["updateWebapp"]["webapp"]["subdomain"]
        )

        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": None}},
        )
        self.assertTrue(response["data"]["updateWebapp"]["success"])
        self.assertIsNone(response["data"]["updateWebapp"]["webapp"]["subdomain"])

    def test_update_webapp_subdomain_not_lowercase(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": "MyWebapp"}},
        )
        self.assertFalse(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            response["data"]["updateWebapp"]["errors"], ["SUBDOMAIN_NOT_LOWERCASE"]
        )

    def test_update_webapp_subdomain_too_short(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": "ab"}},
        )
        self.assertFalse(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            response["data"]["updateWebapp"]["errors"], ["SUBDOMAIN_TOO_SHORT"]
        )

    def test_update_webapp_subdomain_has_dots(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": "my.webapp"}},
        )
        self.assertFalse(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            response["data"]["updateWebapp"]["errors"], ["SUBDOMAIN_HAS_DOTS"]
        )

    def test_update_webapp_subdomain_reserved(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": "admin"}},
        )
        self.assertFalse(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            response["data"]["updateWebapp"]["errors"], ["SUBDOMAIN_RESERVED"]
        )

    def test_update_webapp_subdomain_invalid_format(self):
        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": "-invalid"}},
        )
        self.assertFalse(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            response["data"]["updateWebapp"]["errors"], ["SUBDOMAIN_INVALID_FORMAT"]
        )

    def test_update_webapp_subdomain_already_taken(self):
        self.client.force_login(self.USER_ROOT)
        other_webapp = Webapp.objects.create(
            name="Other Webapp",
            slug="other-webapp",
            url="http://other.com",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
            subdomain="taken",
        )
        response = self.run_query(
            self.UPDATE_WEBAPP_SUBDOMAIN_MUTATION,
            {"input": {"id": str(self.WEBAPP.id), "subdomain": "taken"}},
        )
        self.assertFalse(response["data"]["updateWebapp"]["success"])
        self.assertEqual(
            response["data"]["updateWebapp"]["errors"], ["SUBDOMAIN_ALREADY_TAKEN"]
        )
        other_webapp.delete()

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
