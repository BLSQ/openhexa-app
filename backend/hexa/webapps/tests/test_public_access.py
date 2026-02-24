import requests_mock
from django.core.exceptions import ValidationError

from hexa.core.test import GraphQLTestCase, TestCase
from hexa.superset.models import SupersetInstance
from hexa.user_management.models import (
    Organization,
    User,
)
from hexa.webapps.models import SupersetWebapp, Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class SupersetDashboardViewAccessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORG = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-public",
            organization_type="CORPORATE",
        )
        cls.SUPERSET_INSTANCE = SupersetInstance.objects.create(
            name="Superset",
            url="https://superset.example.com",
            api_username="test",
            api_password="password",
            organization=cls.ORG,
        )
        cls.USER_MEMBER = User.objects.create_user(
            "member@test.com",
            "password",
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "nonmember@test.com",
            "password",
        )
        cls.WORKSPACE = Workspace.objects.create(
            name="Test Workspace",
            organization=cls.ORG,
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.WEBAPP_PRIVATE = SupersetWebapp.create_if_has_perm(
            principal=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            superset_instance=cls.SUPERSET_INSTANCE,
            external_dashboard_id="ext-private",
            name="Private Dashboard",
            created_by=cls.USER_MEMBER,
            is_public=False,
        )
        cls.DASHBOARD_PRIVATE = cls.WEBAPP_PRIVATE.superset_dashboard

        cls.WEBAPP_PUBLIC = SupersetWebapp.create_if_has_perm(
            principal=cls.USER_MEMBER,
            workspace=cls.WORKSPACE,
            superset_instance=cls.SUPERSET_INSTANCE,
            external_dashboard_id="ext-public",
            name="Public Dashboard",
            created_by=cls.USER_MEMBER,
            is_public=True,
        )
        cls.DASHBOARD_PUBLIC = cls.WEBAPP_PUBLIC.superset_dashboard

    def _mock_superset(self, mocker):
        mocker.post(
            "https://superset.example.com/api/v1/security/login",
            json={"access_token": "token"},
        )
        mocker.get(
            "https://superset.example.com/api/v1/security/csrf_token/",
            headers={"Set-Cookie": "cookie"},
            json={"result": "csrf"},
        )
        mocker.post(
            "https://superset.example.com/api/v1/security/guest_token/",
            json={"token": "guest_token"},
        )

    def test_anonymous_cannot_view_private_superset_dashboard(self):
        url = f"/superset/dashboard/{self.DASHBOARD_PRIVATE.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_non_member_cannot_view_private_superset_dashboard(self):
        self.client.force_login(self.USER_NON_MEMBER)
        url = f"/superset/dashboard/{self.DASHBOARD_PRIVATE.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_member_can_view_private_superset_dashboard(self):
        self.client.force_login(self.USER_MEMBER)
        url = f"/superset/dashboard/{self.DASHBOARD_PRIVATE.id}/"
        with requests_mock.Mocker() as mocker:
            self._mock_superset(mocker)
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_can_view_public_superset_dashboard(self):
        url = f"/superset/dashboard/{self.DASHBOARD_PUBLIC.id}/"
        with requests_mock.Mocker() as mocker:
            self._mock_superset(mocker)
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_member_can_view_public_superset_dashboard(self):
        self.client.force_login(self.USER_NON_MEMBER)
        url = f"/superset/dashboard/{self.DASHBOARD_PUBLIC.id}/"
        with requests_mock.Mocker() as mocker:
            self._mock_superset(mocker)
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class IframeWebappAccessTest(GraphQLTestCase):
    WEBAPP_QUERY = """
        query Webapp($workspaceSlug: String!, $slug: String!) {
            webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                id
                name
            }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@iframe-test.com",
            "password",
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "nonmember@iframe-test.com",
            "password",
        )
        cls.WORKSPACE = Workspace.objects.create(name="Iframe Workspace")
        WorkspaceMembership.objects.create(
            user=cls.USER_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WEBAPP_PRIVATE = Webapp.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="Private Iframe",
            created_by=cls.USER_ADMIN,
            url="https://example.com",
            is_public=False,
        )
        cls.WEBAPP_PUBLIC = Webapp.objects.create_if_has_perm(
            cls.USER_ADMIN,
            cls.WORKSPACE,
            name="Public Iframe",
            created_by=cls.USER_ADMIN,
            url="https://example.com",
            is_public=True,
        )

    def _query_webapp(self, webapp):
        return self.run_query(
            self.WEBAPP_QUERY,
            variables={
                "workspaceSlug": self.WORKSPACE.slug,
                "slug": webapp.slug,
            },
        )

    def test_anonymous_cannot_access_private_webapp(self):
        result = self._query_webapp(self.WEBAPP_PRIVATE)
        self.assertIsNone(result["data"]["webapp"])

    def test_anonymous_can_access_public_webapp(self):
        result = self._query_webapp(self.WEBAPP_PUBLIC)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Public Iframe")

    def test_non_member_cannot_access_private_webapp(self):
        self.client.force_login(self.USER_NON_MEMBER)
        result = self._query_webapp(self.WEBAPP_PRIVATE)
        self.assertIsNone(result["data"]["webapp"])

    def test_non_member_can_access_public_webapp(self):
        self.client.force_login(self.USER_NON_MEMBER)
        result = self._query_webapp(self.WEBAPP_PUBLIC)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Public Iframe")

    def test_member_can_access_private_webapp(self):
        self.client.force_login(self.USER_ADMIN)
        result = self._query_webapp(self.WEBAPP_PRIVATE)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Private Iframe")

    def test_member_can_access_public_webapp(self):
        self.client.force_login(self.USER_ADMIN)
        result = self._query_webapp(self.WEBAPP_PUBLIC)
        self.assertIsNotNone(result["data"]["webapp"])
        self.assertEqual(result["data"]["webapp"]["name"], "Public Iframe")


class WebappURLValidationTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("xss@test.com", "password")
        cls.WORKSPACE = Workspace.objects.create(name="XSS Workspace")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def test_create_webapp_with_javascript_url_rejected(self):
        with self.assertRaises(ValidationError):
            Webapp.objects.create_if_has_perm(
                self.USER,
                self.WORKSPACE,
                name="XSS Webapp",
                created_by=self.USER,
                url="javascript:alert('XSS')",
            )

    def test_create_webapp_with_data_url_rejected(self):
        with self.assertRaises(ValidationError):
            Webapp.objects.create_if_has_perm(
                self.USER,
                self.WORKSPACE,
                name="Data Webapp",
                created_by=self.USER,
                url="data:text/html,<script>alert('XSS')</script>",
            )

    def test_create_webapp_with_https_url_accepted(self):
        webapp = Webapp.objects.create_if_has_perm(
            self.USER,
            self.WORKSPACE,
            name="HTTPS Webapp",
            created_by=self.USER,
            url="https://example.com",
        )
        self.assertEqual(webapp.url, "https://example.com")

    def test_update_webapp_with_javascript_url_rejected(self):
        webapp = Webapp.objects.create_if_has_perm(
            self.USER,
            self.WORKSPACE,
            name="Safe Webapp",
            created_by=self.USER,
            url="https://example.com",
        )
        self.client.force_login(self.USER)
        result = self.run_query(
            """
            mutation UpdateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                }
            }
            """,
            variables={
                "input": {
                    "id": str(webapp.id),
                    "source": {"iframe": {"url": "javascript:alert('XSS')"}},
                }
            },
        )
        self.assertFalse(result["data"]["updateWebapp"]["success"])
        self.assertIn("INVALID_URL", result["data"]["updateWebapp"]["errors"])
        webapp.refresh_from_db()
        self.assertEqual(webapp.url, "https://example.com")
