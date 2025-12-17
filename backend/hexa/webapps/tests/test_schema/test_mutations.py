import base64

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappMutationsTest(GraphQLTestCase):
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

    def test_create_iframe_webapp_with_url_succeeds(self):
        """IFRAME webapp can be created with URL"""
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
                        type
                        url
                    }
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": self.WS1.slug,
                    "name": "Test iFrame",
                    "content": {"iframe": {"url": "https://example.com"}},
                }
            },
        )
        self.assertEqual(response["data"]["createWebapp"]["success"], True)
        self.assertEqual(response["data"]["createWebapp"]["webapp"]["type"], "IFRAME")
        self.assertEqual(
            response["data"]["createWebapp"]["webapp"]["url"], "https://example.com"
        )

    def test_create_html_webapp_with_content_succeeds(self):
        """HTML webapp can be created with content"""
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
                        type
                        content
                    }
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": self.WS1.slug,
                    "name": "Test HTML",
                    "content": {"html": {"content": "<h1>Hello World</h1>"}},
                }
            },
        )
        self.assertEqual(response["data"]["createWebapp"]["success"], True)
        self.assertEqual(response["data"]["createWebapp"]["webapp"]["type"], "HTML")
        self.assertEqual(
            response["data"]["createWebapp"]["webapp"]["content"],
            "<h1>Hello World</h1>",
        )

    def test_create_bundle_webapp_with_bundle_succeeds(self):
        """Bundle webapp can be created with bundle"""
        self.client.force_login(self.USER_ROOT)
        bundle_data = b"PK\x03\x04test bundle content"
        bundle_b64 = base64.b64encode(bundle_data).decode("utf-8")

        response = self.run_query(
            """
            mutation createWebapp($input: CreateWebappInput!) {
                createWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        id
                        name
                        type
                    }
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": self.WS1.slug,
                    "name": "Test Bundle",
                    "content": {"bundle": {"bundle": bundle_b64}},
                }
            },
        )
        self.assertEqual(response["data"]["createWebapp"]["success"], True)
        self.assertEqual(response["data"]["createWebapp"]["webapp"]["type"], "BUNDLE")

    def test_update_webapp_name_only_succeeds(self):
        """Updating only the name should work without validation errors"""
        webapp = Webapp.objects.create(
            name="Original Name",
            slug="test-webapp",
            url="https://example.com",
            type="iframe",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
        )

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation updateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        name
                        url
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(webapp.id),
                    "name": "Updated Name",
                }
            },
        )
        self.assertEqual(response["data"]["updateWebapp"]["success"], True)
        self.assertEqual(
            response["data"]["updateWebapp"]["webapp"]["name"], "Updated Name"
        )
        self.assertEqual(
            response["data"]["updateWebapp"]["webapp"]["url"], "https://example.com"
        )

    def test_update_webapp_type_from_html_to_iframe_succeeds(self):
        """Changing type from HTML to IFRAME with URL succeeds"""
        webapp = Webapp.objects.create(
            name="HTML App",
            slug="html-app",
            content="<h1>Test</h1>",
            type="html",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
        )

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation updateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        type
                        url
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(webapp.id),
                    "content": {"iframe": {"url": "https://example.com"}},
                }
            },
        )
        self.assertEqual(response["data"]["updateWebapp"]["success"], True)
        self.assertEqual(response["data"]["updateWebapp"]["webapp"]["type"], "IFRAME")
        self.assertEqual(
            response["data"]["updateWebapp"]["webapp"]["url"], "https://example.com"
        )

    def test_update_webapp_type_from_bundle_to_html_succeeds(self):
        """Changing type from BUNDLE to HTML with content succeeds"""
        bundle_data = b"PK\x03\x04test bundle content"
        webapp = Webapp.objects.create(
            name="Bundle App",
            slug="bundle-app",
            bundle=bundle_data,
            type="bundle",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
        )

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation updateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        type
                        content
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(webapp.id),
                    "content": {"html": {"content": "<h1>New HTML Content</h1>"}},
                }
            },
        )
        self.assertEqual(response["data"]["updateWebapp"]["success"], True)
        self.assertEqual(response["data"]["updateWebapp"]["webapp"]["type"], "HTML")
        self.assertEqual(
            response["data"]["updateWebapp"]["webapp"]["content"],
            "<h1>New HTML Content</h1>",
        )

    def test_update_webapp_type_from_html_to_bundle_succeeds(self):
        """Changing type from HTML to BUNDLE with bundle succeeds"""
        webapp = Webapp.objects.create(
            name="HTML App",
            slug="html-app",
            content="<h1>Test</h1>",
            type="html",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
        )
        bundle_data = b"PK\x03\x04new bundle content"
        bundle_b64 = base64.b64encode(bundle_data).decode("utf-8")

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation updateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        type
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(webapp.id),
                    "content": {"bundle": {"bundle": bundle_b64}},
                }
            },
        )
        self.assertEqual(response["data"]["updateWebapp"]["success"], True)
        self.assertEqual(response["data"]["updateWebapp"]["webapp"]["type"], "BUNDLE")

    def test_update_webapp_type_from_iframe_to_bundle_succeeds(self):
        """Changing type from IFRAME to BUNDLE with bundle succeeds"""
        webapp = Webapp.objects.create(
            name="iFrame App",
            slug="iframe-app",
            url="https://example.com",
            type="iframe",
            workspace=self.WS1,
            created_by=self.USER_ROOT,
        )
        bundle_data = b"PK\x03\x04new bundle content"
        bundle_b64 = base64.b64encode(bundle_data).decode("utf-8")

        self.client.force_login(self.USER_ROOT)
        response = self.run_query(
            """
            mutation updateWebapp($input: UpdateWebappInput!) {
                updateWebapp(input: $input) {
                    success
                    errors
                    webapp {
                        type
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(webapp.id),
                    "content": {"bundle": {"bundle": bundle_b64}},
                }
            },
        )
        self.assertEqual(response["data"]["updateWebapp"]["success"], True)
        self.assertEqual(response["data"]["updateWebapp"]["webapp"]["type"], "BUNDLE")
