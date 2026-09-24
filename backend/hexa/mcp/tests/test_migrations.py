import importlib
from datetime import timedelta

from django.apps import apps as global_apps
from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application

from hexa.mcp.models import MCPConnection
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

migration = importlib.import_module("hexa.mcp.migrations.0002_mcp_connection")


class BackfillConnectionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CREATOR = User.objects.create_user(
            "creator@openhexa.org", "password", is_superuser=True
        )
        cls.USER = User.objects.create_user("member@openhexa.org", "password")
        cls.ORGANIZATION = Organization.objects.create(name="Backfill Org")
        cls.MEMBER_OF = create_workspace(
            cls.CREATOR, name="Member of", organization=cls.ORGANIZATION
        )
        cls.ADMINISTERED = create_workspace(
            cls.CREATOR, name="Administered", organization=cls.ORGANIZATION
        )
        cls.ARCHIVED = create_workspace(
            cls.CREATOR, name="Archived", organization=cls.ORGANIZATION
        )
        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="backfill-test-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        for workspace in (cls.MEMBER_OF, cls.ARCHIVED):
            WorkspaceMembership.objects.create(
                user=cls.USER,
                workspace=workspace,
                role=WorkspaceMembershipRole.EDITOR,
            )
        cls.ARCHIVED.archived = True
        cls.ARCHIVED.save()

    def setUp(self):
        super().setUp()
        MCPConnection.objects.all().delete()

    def give_token(self, user, scope="openhexa:mcp"):
        return AccessToken.objects.create(
            user=user,
            application=self.APPLICATION,
            token=f"token-{user.email}-{scope}",
            scope=scope,
            expires=timezone.now() + timedelta(hours=1),
        )

    def backfill(self):
        migration.backfill_connections(global_apps, None)

    def test_a_token_holder_gets_a_connection_with_every_tool(self):
        self.give_token(self.USER)

        self.backfill()

        connection = MCPConnection.objects.get(user=self.USER)
        self.assertEqual(sorted(migration.ALL_TOOLS), sorted(connection.tools))

    def test_a_token_for_another_scope_is_ignored(self):
        self.give_token(self.USER, scope="openhexa:git")

        self.backfill()

        self.assertFalse(MCPConnection.objects.exists())

    def test_it_grants_the_workspaces_the_person_belongs_to(self):
        self.give_token(self.USER)

        self.backfill()

        connection = MCPConnection.objects.get(user=self.USER)
        self.assertEqual([self.MEMBER_OF], list(connection.workspaces.all()))

    def test_archived_workspaces_are_left_out(self):
        self.give_token(self.USER)

        self.backfill()

        connection = MCPConnection.objects.get(user=self.USER)
        self.assertNotIn(self.ARCHIVED, connection.workspaces.all())

    def test_organization_admins_get_the_workspaces_they_administer(self):
        OrganizationMembership.objects.create(
            user=self.USER,
            organization=self.ORGANIZATION,
            role=OrganizationMembershipRole.ADMIN,
        )
        self.give_token(self.USER)

        self.backfill()

        connection = MCPConnection.objects.get(user=self.USER)
        self.assertIn(self.ADMINISTERED, connection.workspaces.all())

    def test_plain_organization_members_do_not(self):
        OrganizationMembership.objects.create(
            user=self.USER,
            organization=self.ORGANIZATION,
            role=OrganizationMembershipRole.MEMBER,
        )
        self.give_token(self.USER)

        self.backfill()

        connection = MCPConnection.objects.get(user=self.USER)
        self.assertNotIn(self.ADMINISTERED, connection.workspaces.all())

    def test_a_superuser_keeps_reaching_everything(self):
        self.give_token(self.CREATOR)

        self.backfill()

        connection = MCPConnection.objects.get(user=self.CREATOR)
        self.assertIn(self.ADMINISTERED, connection.workspaces.all())
        self.assertIn(self.MEMBER_OF, connection.workspaces.all())
        self.assertNotIn(self.ARCHIVED, connection.workspaces.all())

    def test_running_it_twice_changes_nothing(self):
        self.give_token(self.USER)

        self.backfill()
        self.backfill()

        self.assertEqual(1, MCPConnection.objects.filter(user=self.USER).count())
