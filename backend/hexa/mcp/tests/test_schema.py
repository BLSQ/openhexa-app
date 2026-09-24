from datetime import timedelta

from django.utils import timezone
from oauth2_provider.models import AccessToken, Application

from hexa.core.test import GraphQLTestCase
from hexa.mcp.models import MCPConnection
from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

CONNECTIONS_QUERY = """
    query {
        mcpConnections {
            id
            name
            workspaces { slug }
            tools
        }
    }
"""

UPDATE_MUTATION = """
    mutation update($input: UpdateMCPConnectionInput!) {
        updateMCPConnection(input: $input) {
            success
            errors
            mcpConnection { workspaces { slug } tools }
        }
    }
"""

AUTHORIZE_MUTATION = """
    mutation authorize($input: AuthorizeMCPConnectionInput!) {
        authorizeMCPConnection(input: $input) {
            success
            errors
            mcpConnection { tools workspaces { slug } }
        }
    }
"""

REVOKE_MUTATION = """
    mutation revoke($input: RevokeMCPConnectionInput!) {
        revokeMCPConnection(input: $input) { success errors }
    }
"""


class MCPConnectionSchemaTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CREATOR = User.objects.create_user(
            "creator@openhexa.org", "password", is_superuser=True
        )
        cls.USER = User.objects.create_user("owner@openhexa.org", "password")
        cls.OTHER_USER = User.objects.create_user("other@openhexa.org", "password")
        cls.WORKSPACE = create_workspace(cls.CREATOR, name="Malaria")
        cls.FOREIGN_WORKSPACE = create_workspace(cls.CREATOR, name="Foreign")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.EDITOR,
        )

        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="schema-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        cls.CONNECTION = MCPConnection.objects.create(
            user=cls.USER,
            application=cls.APPLICATION,
            tools=["list_files", "read_file"],
        )

    def live_token(self, application=None):
        return AccessToken.objects.create(
            user=self.USER,
            application=application or self.APPLICATION,
            token=f"token-{timezone.now().timestamp()}",
            scope="openhexa:mcp",
            expires=timezone.now() + timedelta(hours=1),
        )

    def test_a_connection_reports_the_tools_it_was_granted(self):
        self.live_token()
        self.client.force_login(self.USER)

        result = self.run_query(CONNECTIONS_QUERY)

        connections = result["data"]["mcpConnections"]
        self.assertEqual(1, len(connections))
        self.assertEqual("Claude", connections[0]["name"])
        self.assertEqual(["list_files", "read_file"], connections[0]["tools"])

    def test_a_connection_with_no_live_token_is_not_listed(self):
        self.client.force_login(self.USER)

        result = self.run_query(CONNECTIONS_QUERY)

        self.assertEqual([], result["data"]["mcpConnections"])

    def test_an_expired_token_does_not_keep_a_connection_listed(self):
        AccessToken.objects.create(
            user=self.USER,
            application=self.APPLICATION,
            token="stale",
            scope="openhexa:mcp",
            expires=timezone.now() - timedelta(hours=1),
        )
        self.client.force_login(self.USER)

        result = self.run_query(CONNECTIONS_QUERY)

        self.assertEqual([], result["data"]["mcpConnections"])

    def test_an_archived_workspace_is_not_reported_as_granted(self):
        self.CONNECTION.workspaces.set([self.WORKSPACE])
        self.WORKSPACE.archived = True
        self.WORKSPACE.save()
        self.live_token()
        self.client.force_login(self.USER)

        result = self.run_query(CONNECTIONS_QUERY)

        self.assertEqual([], result["data"]["mcpConnections"][0]["workspaces"])

    def test_connections_are_private_to_their_owner(self):
        self.live_token()
        self.client.force_login(self.OTHER_USER)

        result = self.run_query(CONNECTIONS_QUERY)

        self.assertEqual([], result["data"]["mcpConnections"])

    def test_tools_and_workspaces_can_be_narrowed(self):
        self.live_token()
        self.client.force_login(self.USER)

        result = self.run_query(
            UPDATE_MUTATION,
            {
                "input": {
                    "id": str(self.CONNECTION.id),
                    "workspaceSlugs": [self.WORKSPACE.slug],
                    "tools": ["write_file", "list_files"],
                }
            },
        )

        payload = result["data"]["updateMCPConnection"]
        self.assertTrue(payload["success"], payload["errors"])
        self.assertEqual(
            [{"slug": self.WORKSPACE.slug}], payload["mcpConnection"]["workspaces"]
        )
        self.CONNECTION.refresh_from_db()
        self.assertEqual(["list_files", "write_file"], self.CONNECTION.tools)

    def test_saved_workspaces_come_back_in_a_stable_order(self):
        self.live_token()
        second = create_workspace(self.CREATOR, name="Aardvark")
        WorkspaceMembership.objects.create(
            user=self.USER, workspace=second, role=WorkspaceMembershipRole.EDITOR
        )
        self.client.force_login(self.USER)

        result = self.run_query(
            UPDATE_MUTATION,
            {
                "input": {
                    "id": str(self.CONNECTION.id),
                    "workspaceSlugs": [self.WORKSPACE.slug, second.slug],
                }
            },
        )

        slugs = [
            workspace["slug"]
            for workspace in result["data"]["updateMCPConnection"]["mcpConnection"][
                "workspaces"
            ]
        ]
        self.assertEqual([second.slug, self.WORKSPACE.slug], slugs)

    def test_an_unknown_tool_name_is_refused(self):
        self.live_token()
        self.client.force_login(self.USER)

        result = self.run_query(
            UPDATE_MUTATION,
            {"input": {"id": str(self.CONNECTION.id), "tools": ["rm_minus_rf"]}},
        )

        payload = result["data"]["updateMCPConnection"]
        self.assertFalse(payload["success"])
        self.assertEqual(["TOOL_NOT_FOUND"], payload["errors"])

    def test_a_workspace_the_user_cannot_reach_is_refused(self):
        self.live_token()
        self.client.force_login(self.USER)

        result = self.run_query(
            UPDATE_MUTATION,
            {
                "input": {
                    "id": str(self.CONNECTION.id),
                    "workspaceSlugs": [self.FOREIGN_WORKSPACE.slug],
                }
            },
        )

        payload = result["data"]["updateMCPConnection"]
        self.assertFalse(payload["success"])
        self.assertEqual(["WORKSPACE_NOT_FOUND"], payload["errors"])

    def test_another_users_connection_cannot_be_edited(self):
        self.client.force_login(self.OTHER_USER)

        result = self.run_query(
            UPDATE_MUTATION,
            {"input": {"id": str(self.CONNECTION.id), "tools": ["read_file"]}},
        )

        payload = result["data"]["updateMCPConnection"]
        self.assertFalse(payload["success"])
        self.assertEqual(["NOT_FOUND"], payload["errors"])
        self.CONNECTION.refresh_from_db()
        self.assertEqual(["list_files", "read_file"], self.CONNECTION.tools)

    def test_revoking_removes_the_grant_and_its_live_tokens(self):
        AccessToken.objects.create(
            user=self.USER,
            application=self.APPLICATION,
            token="live-token",
            scope="openhexa:mcp",
            expires=timezone.now() + timedelta(hours=1),
        )
        self.client.force_login(self.USER)

        result = self.run_query(
            REVOKE_MUTATION, {"input": {"id": str(self.CONNECTION.id)}}
        )

        self.assertTrue(result["data"]["revokeMCPConnection"]["success"])
        self.assertFalse(MCPConnection.objects.filter(pk=self.CONNECTION.pk).exists())
        self.assertFalse(
            AccessToken.objects.filter(application=self.APPLICATION).exists()
        )


class AuthorizeMCPConnectionTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CREATOR = User.objects.create_user(
            "creator@openhexa.org", "password", is_superuser=True
        )
        cls.USER = User.objects.create_user("consent@openhexa.org", "password")
        cls.WORKSPACE = create_workspace(cls.CREATOR, name="Malaria")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="consent-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

    def authorize(self, **input):
        return self.run_query(
            AUTHORIZE_MUTATION,
            {"input": {"clientId": self.APPLICATION.client_id, **input}},
        )["data"]["authorizeMCPConnection"]

    def test_a_first_authorization_creates_the_connection(self):
        self.client.force_login(self.USER)

        payload = self.authorize(
            tools=["list_files"],
            workspaceSlugs=[self.WORKSPACE.slug],
        )

        self.assertTrue(payload["success"], payload["errors"])
        connection = MCPConnection.objects.get(
            user=self.USER, application=self.APPLICATION
        )
        self.assertEqual(["list_files"], connection.tools)
        self.assertEqual([self.WORKSPACE], list(connection.workspaces.all()))

    def test_authorizing_again_replaces_the_grant(self):
        self.client.force_login(self.USER)
        self.authorize(tools=["list_files"])

        payload = self.authorize(tools=["read_file"])

        self.assertTrue(payload["success"], payload["errors"])
        self.assertEqual(
            1,
            MCPConnection.objects.filter(
                user=self.USER, application=self.APPLICATION
            ).count(),
        )
        self.assertEqual(["read_file"], payload["mcpConnection"]["tools"])

    def test_authorizing_a_re_registered_client_cuts_off_the_old_one(self):
        old_application = Application.objects.create(
            name=self.APPLICATION.name,
            client_id="consent-test-client-old",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        old = MCPConnection.objects.create(
            user=self.USER, application=old_application, tools=["list_files"]
        )
        self.client.force_login(self.USER)

        self.authorize(tools=["list_files"])

        self.assertFalse(MCPConnection.objects.filter(pk=old.pk).exists())

    def test_an_unknown_client_is_refused(self):
        self.client.force_login(self.USER)

        payload = self.run_query(
            AUTHORIZE_MUTATION, {"input": {"clientId": "nope", "tools": []}}
        )["data"]["authorizeMCPConnection"]

        self.assertFalse(payload["success"])
        self.assertEqual(["CLIENT_NOT_FOUND"], payload["errors"])
        self.assertFalse(MCPConnection.objects.exists())

    def test_a_workspace_the_user_cannot_reach_is_refused(self):
        foreign = create_workspace(self.CREATOR, name="Foreign")
        self.client.force_login(self.USER)

        payload = self.authorize(workspaceSlugs=[foreign.slug])

        self.assertFalse(payload["success"])
        self.assertEqual(["WORKSPACE_NOT_FOUND"], payload["errors"])


class MCPAuthorizationRequestTest(GraphQLTestCase):
    """The consent screen reads its context from this query."""

    AUTHORIZATION_REQUEST_QUERY = """
        query request($clientId: String!) {
            mcpAuthorizationRequest(clientId: $clientId) {
                clientName
                connection { tools }
                tools { name resource }
            }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("request@openhexa.org", "password")
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="request-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

    def request(self, client_id):
        return self.run_query(
            self.AUTHORIZATION_REQUEST_QUERY, {"clientId": client_id}
        )["data"]["mcpAuthorizationRequest"]

    def test_a_first_authorization_has_no_connection_yet(self):
        self.client.force_login(self.USER)

        payload = self.request(self.APPLICATION.client_id)

        self.assertEqual("Claude", payload["clientName"])
        self.assertIsNone(payload["connection"])
        self.assertTrue(len(payload["tools"]) > 0)

    def test_re_authorizing_shows_the_grant_as_it_stands(self):
        MCPConnection.objects.create(
            user=self.USER, application=self.APPLICATION, tools=["list_files"]
        )
        self.client.force_login(self.USER)

        payload = self.request(self.APPLICATION.client_id)

        self.assertEqual(["list_files"], payload["connection"]["tools"])

    def test_an_unknown_client_returns_nothing(self):
        self.client.force_login(self.USER)

        self.assertIsNone(self.request("nope"))
