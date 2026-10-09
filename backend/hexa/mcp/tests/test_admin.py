from django.urls import reverse
from oauth2_provider.models import Application

from hexa.mcp.models import MCPConnection
from hexa.user_management.models import User

from .testutils import MCPTestCase


class MCPConnectionAdminTest(MCPTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.STAFF = User.objects.create_user(
            "staff@openhexa.org", "password", is_staff=True, is_superuser=True
        )
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="admin-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        cls.GRANT = MCPConnection.objects.create(
            user=cls.USER_VIEWER, application=cls.APPLICATION, tools=["list_files"]
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.STAFF)

    def test_the_list_and_detail_pages_render(self):
        response = self.client.get(reverse("admin:mcp_mcpconnection_changelist"))
        self.assertContains(response, "viewer@openhexa.org")

        response = self.client.get(
            reverse("admin:mcp_mcpconnection_change", args=[self.GRANT.pk])
        )
        self.assertContains(response, "list_files")
