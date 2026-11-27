from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import Organization, User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WorkspaceAdminChangelistTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.STAFF = User.objects.create_user(
            "staff@openhexa.org", "password", is_staff=True, is_superuser=True
        )
        cls.JANE = User.objects.create_user("jane@openhexa.org", "password")
        cls.JOHN = User.objects.create_user("john@openhexa.org", "password")
        organization = Organization.objects.create(name="Org")
        cls.MALARIA = Workspace.objects.create(
            name="Malaria", slug="malaria", db_name="malaria", organization=organization
        )
        cls.HIV = Workspace.objects.create(
            name="HIV", slug="hiv", db_name="hiv", organization=organization
        )
        cls.JANE_MEMBERSHIP = WorkspaceMembership.objects.create(
            workspace=cls.MALARIA, user=cls.JANE, role=WorkspaceMembershipRole.ADMIN
        )
        cls.JOHN_MEMBERSHIP = WorkspaceMembership.objects.create(
            workspace=cls.HIV, user=cls.JOHN, role=WorkspaceMembershipRole.VIEWER
        )
        cls.PENDING_INVITATION = WorkspaceInvitation.objects.create(
            email="pending@openhexa.org",
            workspace=cls.MALARIA,
            invited_by=cls.JANE,
            role=WorkspaceMembershipRole.VIEWER,
        )
        cls.ACCEPTED_INVITATION = WorkspaceInvitation.objects.create(
            email="accepted@openhexa.org",
            workspace=cls.HIV,
            invited_by=cls.JOHN,
            role=WorkspaceMembershipRole.VIEWER,
            status=WorkspaceInvitationStatus.ACCEPTED,
        )
        cls.DHIS2 = Connection.objects.create(
            workspace=cls.MALARIA,
            user=cls.JANE,
            name="DHIS2 production",
            slug="dhis2-production",
            connection_type=ConnectionType.DHIS2,
        )
        cls.POSTGRES = Connection.objects.create(
            workspace=cls.HIV,
            user=cls.JOHN,
            name="Warehouse",
            slug="warehouse",
            connection_type=ConnectionType.POSTGRESQL,
        )

    def setUp(self):
        self.client.force_login(self.STAFF)

    def assertChangelist(self, model, params, expected):
        response = self.client.get(
            reverse(f"admin:workspaces_{model}_changelist"), params
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context_data["cl"].result_list), expected)

    def test_memberships_can_be_filtered_and_searched(self):
        self.assertChangelist(
            "workspacemembership", {"role__exact": "ADMIN"}, {self.JANE_MEMBERSHIP}
        )
        self.assertChangelist(
            "workspacemembership", {"q": "jane@"}, {self.JANE_MEMBERSHIP}
        )
        self.assertChangelist(
            "workspacemembership", {"q": "hiv"}, {self.JOHN_MEMBERSHIP}
        )

    def test_invitations_can_be_filtered_and_searched(self):
        self.assertChangelist(
            "workspaceinvitation",
            {"status__exact": "PENDING"},
            {self.PENDING_INVITATION},
        )
        self.assertChangelist(
            "workspaceinvitation", {"q": "john@"}, {self.ACCEPTED_INVITATION}
        )
        self.assertChangelist(
            "workspaceinvitation", {"q": "malaria"}, {self.PENDING_INVITATION}
        )

    def test_connections_can_be_searched(self):
        self.assertChangelist("connection", {"q": "dhis2"}, {self.DHIS2})
        self.assertChangelist("connection", {"q": "hiv"}, {self.POSTGRES})
