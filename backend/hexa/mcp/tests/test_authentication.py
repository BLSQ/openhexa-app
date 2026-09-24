from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application

from hexa.core.middlewares import oauth2_token_authentication_middleware
from hexa.mcp.models import MCPConnection, MCPUser
from hexa.mcp.tests.testutils import all_tool_names
from hexa.user_management.models import (
    Organization,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace


class MCPUserFilteringTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.SUPERUSER = User.objects.create_user(
            "root@bluesquarehub.com", "password", is_superuser=True
        )
        cls.USER = User.objects.create_user("mcp@bluesquarehub.com", "password")
        cls.ORGANIZATION = Organization.objects.create(name="MCP Org")
        cls.GRANTED = create_workspace(
            cls.SUPERUSER, name="Granted", organization=cls.ORGANIZATION
        )
        cls.MEMBER_ONLY = create_workspace(
            cls.SUPERUSER, name="Member only", organization=cls.ORGANIZATION
        )
        cls.STRANGER = create_workspace(
            cls.SUPERUSER, name="Stranger", organization=cls.ORGANIZATION
        )
        for workspace in (cls.GRANTED, cls.MEMBER_ONLY):
            WorkspaceMembership.objects.create(
                user=cls.USER,
                workspace=workspace,
                role=WorkspaceMembershipRole.EDITOR,
            )

        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="mcp-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

    def connection_for(self, user, *workspaces):
        connection = MCPConnection.objects.create(
            user=user,
            application=self.APPLICATION,
            tools=all_tool_names(),
        )
        connection.workspaces.set(workspaces)
        return connection

    def test_workspace_ids_are_the_granted_workspaces(self):
        connection = self.connection_for(self.USER, self.GRANTED)
        mcp_user = MCPUser.from_user(self.USER, connection)

        self.assertEqual([self.GRANTED.pk], mcp_user.workspace_ids)
        self.assertEqual(self.USER, mcp_user.real_user)

    def test_grant_narrows_to_the_granted_workspaces(self):
        connection = self.connection_for(self.USER, self.GRANTED)
        mcp_user = MCPUser.from_user(self.USER, connection)

        self.assertEqual(
            [self.GRANTED],
            list(Workspace.objects.filter_for_user(mcp_user)),
        )
        self.assertIn(self.MEMBER_ONLY, Workspace.objects.filter_for_user(self.USER))

    def test_grant_cannot_widen_beyond_the_user_memberships(self):
        connection = self.connection_for(self.USER, self.GRANTED, self.STRANGER)
        mcp_user = MCPUser.from_user(self.USER, connection)

        self.assertEqual(
            [self.GRANTED],
            list(Workspace.objects.filter_for_user(mcp_user)),
        )

    def test_grant_narrows_a_superuser_too(self):
        connection = self.connection_for(self.SUPERUSER, self.GRANTED)
        mcp_user = MCPUser.from_user(self.SUPERUSER, connection)

        self.assertEqual(
            [self.GRANTED],
            list(Workspace.objects.filter_for_user(mcp_user)),
        )
        self.assertIn(self.STRANGER, Workspace.objects.filter_for_user(self.SUPERUSER))

    def test_no_granted_workspace_sees_nothing(self):
        connection = self.connection_for(self.USER)
        mcp_user = MCPUser.from_user(self.USER, connection)

        self.assertEqual([], list(Workspace.objects.filter_for_user(mcp_user)))


class MCPConnectionAccessTest(TestCase):
    def test_only_the_named_tools_are_allowed(self):
        connection = MCPConnection(tools=["list_files", "read_file"])

        self.assertTrue(connection.allows_tool("list_files"))
        self.assertFalse(connection.allows_tool("write_file"))

    def test_a_full_grant_does_not_cover_tools_added_later(self):
        connection = MCPConnection(tools=all_tool_names())

        self.assertTrue(connection.allows_tool("write_file"))
        self.assertFalse(connection.allows_tool("a_tool_shipped_next_release"))

    def test_an_empty_grant_allows_nothing(self):
        connection = MCPConnection(tools=[])

        self.assertFalse(connection.allows_tool("list_files"))


class MCPTokenMiddlewareTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("token@bluesquarehub.com", "password")
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="token-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        cls.TOKEN = AccessToken.objects.create(
            user=cls.USER,
            application=cls.APPLICATION,
            token="a-token",
            scope="openhexa:mcp",
            expires=timezone.now() + timedelta(hours=1),
        )

    def call(self):
        request = RequestFactory().post(
            "/mcp/", HTTP_AUTHORIZATION=f"Bearer {self.TOKEN.token}"
        )
        request.user = AnonymousUser()
        oauth2_token_authentication_middleware(lambda r: r)(request)
        return request.user

    def test_a_token_without_a_grant_authenticates_nobody(self):
        self.assertFalse(self.call().is_authenticated)

    def test_a_token_with_a_grant_acts_under_it(self):
        connection = MCPConnection.objects.create(
            user=self.USER, application=self.APPLICATION, tools=all_tool_names()
        )

        user = self.call()

        self.assertIsInstance(user, MCPUser)
        self.assertEqual(connection, user.connection)
        self.assertEqual(self.USER, user.real_user)
        connection.refresh_from_db()
        self.assertIsNotNone(connection.last_used_at)
