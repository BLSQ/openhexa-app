from django.urls import reverse
from oauth2_provider.models import Application

from hexa.mcp.models import MCPConnection, ToolCall
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


class ToolCallAdminTest(MCPTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.STAFF = User.objects.create_user(
            "staff@openhexa.org", "password", is_staff=True, is_superuser=True
        )
        cls.VIEWER_CALL = ToolCall.objects.create(
            user=cls.USER_VIEWER,
            tool_name="list_files",
            arguments={"workspace_slug": "viewer-workspace"},
            success=True,
        )
        cls.ADMIN_CALL = ToolCall.objects.create(
            user=cls.USER_ADMIN,
            tool_name="run_pipeline",
            arguments={"pipeline_id": "abc"},
            success=False,
            error="Pipeline not found",
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.STAFF)

    def _listed_calls(self, **params):
        response = self.client.get(reverse("admin:mcp_toolcall_changelist"), params)
        self.assertEqual(response.status_code, 200)
        return list(response.context["cl"].result_list)

    def test_the_list_and_detail_pages_render(self):
        response = self.client.get(reverse("admin:mcp_toolcall_changelist"))
        self.assertContains(response, "viewer-workspace")
        self.assertContains(response, "Pipeline not found")

        response = self.client.get(
            reverse("admin:mcp_toolcall_change", args=[self.VIEWER_CALL.pk])
        )
        self.assertContains(response, "list_files")

    def test_tool_calls_are_read_only(self):
        response = self.client.get(reverse("admin:mcp_toolcall_add"))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse("admin:mcp_toolcall_change", args=[self.VIEWER_CALL.pk]),
            {"tool_name": "changed"},
        )
        self.assertEqual(response.status_code, 403)
        self.VIEWER_CALL.refresh_from_db()
        self.assertEqual(self.VIEWER_CALL.tool_name, "list_files")

    def test_search_by_user_email(self):
        self.assertEqual(
            self._listed_calls(q=self.USER_VIEWER.email), [self.VIEWER_CALL]
        )

    def test_search_in_arguments_and_error(self):
        self.assertEqual(self._listed_calls(q="viewer-workspace"), [self.VIEWER_CALL])
        self.assertEqual(self._listed_calls(q="not found"), [self.ADMIN_CALL])

    def test_filter_by_user(self):
        self.assertEqual(
            self._listed_calls(user__id__exact=self.USER_ADMIN.pk), [self.ADMIN_CALL]
        )
