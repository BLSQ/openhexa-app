from django.test import override_settings

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

STATIC_URL = "http://static-b.webapps.localhost:8000/page.html?tab=2"


@override_settings(WEBAPPS_DOMAIN="webapps.localhost:8000", ALLOWED_HOSTS=["*"])
class IframeWebappRedirectTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("redirect@test.com", "password")
        cls.WORKSPACE = create_workspace(name="WS Redirect", slug="ws-redirect")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )
        Webapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Custom domain static",
            slug="custom-static",
            subdomain="custom-static",
            custom_domain="dashboard.example.org",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
        )
        cls.IFRAME = Webapp.objects.create(
            workspace=cls.WORKSPACE,
            name="Iframe",
            slug="iframe",
            subdomain="iframe",
            type=Webapp.WebappType.IFRAME,
            url=STATIC_URL,
            is_public=True,
            created_by=cls.USER,
        )

    def _set_url(self, url):
        self.IFRAME.url = url
        self.IFRAME.save()

    def test_points_to_openhexa_webapp_subdomain(self):
        self.assertTrue(self.IFRAME.points_to_openhexa_webapp)

    def test_points_to_openhexa_webapp_custom_domain(self):
        self._set_url("https://dashboard.example.org/")
        self.assertTrue(self.IFRAME.points_to_openhexa_webapp)

    def test_does_not_point_to_openhexa_webapp_for_external_url(self):
        for url in ("https://example.com/", "https://webapps.localhost.evil.com/"):
            with self.subTest(url=url):
                self._set_url(url)
                self.assertFalse(self.IFRAME.points_to_openhexa_webapp)

    def test_subdomain_redirects_to_embedded_openhexa_webapp(self):
        response = self.client.get("/", HTTP_HOST="iframe.webapps.localhost:8000")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], STATIC_URL)

    def test_subdomain_frames_external_url(self):
        self._set_url("https://example.com/")

        response = self.client.get("/", HTTP_HOST="iframe.webapps.localhost:8000")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<iframe src="https://example.com/"', response.content)

    def test_graphql_exposes_points_to_openhexa_webapp(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            """
            query webapp($workspaceSlug: String!, $slug: String!) {
                webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                    pointsToOpenhexaWebapp
                }
            }
            """,
            {"workspaceSlug": self.WORKSPACE.slug, "slug": self.IFRAME.slug},
        )

        self.assertTrue(response["data"]["webapp"]["pointsToOpenhexaWebapp"])
