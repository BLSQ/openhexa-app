from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import (
    Organization,
    OrganizationInvitation,
    OrganizationInvitationStatus,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


class OrganizationTestMixin:
    @staticmethod
    def create_user(email, *args, password=None, **kwargs):
        password = password or "Pa$$w0rd"
        user = User.objects.create_user(email, *args, password=password, **kwargs)
        return user

    @staticmethod
    def create_organization(
        principal: User, name, description="", organization_type="CORPORATE", **kwargs
    ):
        organization = Organization.objects.create(
            name=name,
            description=description,
            organization_type=organization_type,
            **kwargs,
        )
        OrganizationMembership.objects.create(
            organization=organization,
            user=principal,
            role=OrganizationMembershipRole.OWNER,
        )
        return organization

    @staticmethod
    def join_organization(
        user: User, organization: Organization, role: OrganizationMembershipRole
    ):
        membership, created = OrganizationMembership.objects.get_or_create(
            organization=organization, user=user, defaults={"role": role}
        )
        if not created:
            membership.role = role
            membership.save()
        return membership

    @staticmethod
    def create_workspace(principal: User, organization, name, description, **kwargs):
        workspace = Workspace.objects.create_if_has_perm(
            principal=principal,
            organization=organization,
            name=name,
            description=description,
            **kwargs,
        )
        return workspace


class OrganizationMemberTest(GraphQLTestCase, OrganizationTestMixin):
    def setUp(self):
        super().setUp()
        self.owner = self.create_user("owner@blsq.org")
        self.admin = self.create_user("admin@blsq.org")
        self.member = self.create_user("member@blsq.org")
        self.other_member = self.create_user("other_member@blsq.org")
        self.non_member = self.create_user("non_member@blsq.org")

        self.organization = self.create_organization(
            self.owner, "Test Organization", "Description"
        )
        self.admin_membership = self.join_organization(
            self.admin, self.organization, OrganizationMembershipRole.ADMIN
        )
        self.member_membership = self.join_organization(
            self.member, self.organization, OrganizationMembershipRole.MEMBER
        )
        self.other_member_membership = self.join_organization(
            self.other_member, self.organization, OrganizationMembershipRole.MEMBER
        )

    def test_update_organization_member(self):
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganizationMember($input: UpdateOrganizationMemberInput!) {
                updateOrganizationMember(input: $input) {
                    membership {
                        role
                        user {
                            email
                        }
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.member_membership.id),
                    "role": "ADMIN",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "membership": {
                    "role": "ADMIN",
                    "user": {"email": "member@blsq.org"},
                },
            },
            r["data"]["updateOrganizationMember"],
        )

        self.member_membership.refresh_from_db()
        self.assertEqual(self.member_membership.role, OrganizationMembershipRole.ADMIN)

    def test_update_organization_member_unauthorized(self):
        self.client.force_login(self.non_member)
        r = self.run_query(
            """
            mutation UpdateOrganizationMember($input: UpdateOrganizationMemberInput!) {
                updateOrganizationMember(input: $input) {
                    membership {
                        id
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.member_membership.id),
                    "role": "ADMIN",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "membership": None,
            },
            r["data"]["updateOrganizationMember"],
        )

    def test_update_organization_member_by_member(self):
        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation UpdateOrganizationMember($input: UpdateOrganizationMemberInput!) {
                updateOrganizationMember(input: $input) {
                    membership {
                        id
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.other_member_membership.id),
                    "role": "ADMIN",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "membership": None,
            },
            r["data"]["updateOrganizationMember"],
        )

    def test_delete_organization_member(self):
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation DeleteOrganizationMember($input: DeleteOrganizationMemberInput!) {
                deleteOrganizationMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.member_membership.id),
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteOrganizationMember"],
        )
        self.assertFalse(
            OrganizationMembership.objects.filter(id=self.member_membership.id).exists()
        )

    def test_delete_organization_member_unauthorized(self):
        self.client.force_login(self.non_member)
        r = self.run_query(
            """
            mutation DeleteOrganizationMember($input: DeleteOrganizationMemberInput!) {
                deleteOrganizationMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.member_membership.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteOrganizationMember"],
        )

    def test_delete_organization_member_by_member(self):
        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation DeleteOrganizationMember($input: DeleteOrganizationMemberInput!) {
                deleteOrganizationMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(self.other_member_membership.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteOrganizationMember"],
        )

    def test_organization_members_query(self):
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            query OrganizationMembers($organizationId: UUID!) {
                organization(id: $organizationId) {
                    members {
                        items {
                            id
                            role
                            user {
                                email
                            }
                        }
                    }
                }
            }
            """,
            {"organizationId": str(self.organization.id)},
        )

        member_emails = {
            member["user"]["email"]
            for member in r["data"]["organization"]["members"]["items"]
        }
        expected_emails = {
            "owner@blsq.org",
            "admin@blsq.org",
            "member@blsq.org",
            "other_member@blsq.org",
        }
        self.assertEqual(member_emails, expected_emails)


class OrganizationInvitationTest(GraphQLTestCase, OrganizationTestMixin):
    def setUp(self):
        super().setUp()
        self.owner = self.create_user("owner@blsq.org")
        self.member = self.create_user("member@blsq.org")

        self.organization = self.create_organization(
            self.owner, "Test Organization", "Description"
        )
        self.member_membership = self.join_organization(
            self.member, self.organization, OrganizationMembershipRole.MEMBER
        )
        self.workspace = self.create_workspace(
            self.owner,
            self.organization,
            "some_workspace",
            "Some workspace description",
        )

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_invite_organization_member(self, mock_send_invite):
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation InviteOrganizationMember($input: InviteOrganizationMemberInput!) {
                inviteOrganizationMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.organization.id),
                    "userEmail": "invitee@blsq.org",
                    "organizationRole": OrganizationMembershipRole.MEMBER.upper(),
                    "workspaceInvitations": [
                        {
                            "workspaceSlug": self.workspace.slug,
                            "workspaceName": self.workspace.name,
                            "role": WorkspaceMembershipRole.VIEWER,
                        }
                    ],
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["inviteOrganizationMember"],
        )

        invitation = OrganizationInvitation.objects.get(email="invitee@blsq.org")
        self.assertEqual(invitation.organization, self.organization)
        self.assertEqual(invitation.role, OrganizationMembershipRole.MEMBER)
        self.assertEqual(invitation.status, OrganizationInvitationStatus.PENDING)
        workspace_invitations = invitation.workspace_invitations.all()
        self.assertEqual(workspace_invitations.count(), 1)
        self.assertEqual(
            workspace_invitations.first().workspace.slug, self.workspace.slug
        )
        self.assertEqual(
            workspace_invitations.first().workspace.name, self.workspace.name
        )
        self.assertEqual(
            workspace_invitations.first().role, WorkspaceMembershipRole.VIEWER
        )
        mock_send_invite.assert_called_once()

    def test_invite_organization_member_unauthorized(self):
        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation InviteOrganizationMember($input: InviteOrganizationMemberInput!) {
                inviteOrganizationMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.organization.id),
                    "userEmail": "invitee@blsq.org",
                    "organizationRole": OrganizationMembershipRole.MEMBER.upper(),
                    "workspaceInvitations": [],
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["inviteOrganizationMember"],
        )

    def test_invite_existing_member(self):
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation InviteOrganizationMember($input: InviteOrganizationMemberInput!) {
                inviteOrganizationMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.organization.id),
                    "userEmail": "member@blsq.org",
                    "organizationRole": OrganizationMembershipRole.ADMIN.upper(),
                    "workspaceInvitations": [],
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["ALREADY_MEMBER"],
            },
            r["data"]["inviteOrganizationMember"],
        )

    def test_delete_organization_invitation(self):
        invitation = OrganizationInvitation.objects.create(
            email="invitee@blsq.org",
            organization=self.organization,
            invited_by=self.owner,
            role=OrganizationMembershipRole.MEMBER,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation DeleteOrganizationInvitation($input: DeleteOrganizationInvitationInput!) {
                deleteOrganizationInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(invitation.id),
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteOrganizationInvitation"],
        )
        self.assertFalse(
            OrganizationInvitation.objects.filter(id=invitation.id).exists()
        )

    def test_delete_organization_invitation_unauthorized(self):
        invitation = OrganizationInvitation.objects.create(
            email="invitee@blsq.org",
            organization=self.organization,
            invited_by=self.owner,
            role=OrganizationMembershipRole.MEMBER,
        )

        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation DeleteOrganizationInvitation($input: DeleteOrganizationInvitationInput!) {
                deleteOrganizationInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(invitation.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteOrganizationInvitation"],
        )

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_resend_organization_invitation(self, mock_send_invite):
        invitation = OrganizationInvitation.objects.create(
            email="invitee@blsq.org",
            organization=self.organization,
            invited_by=self.owner,
            role=OrganizationMembershipRole.MEMBER,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation ResendOrganizationInvitation($input: ResendOrganizationInvitationInput!) {
                resendOrganizationInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(invitation.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["resendOrganizationInvitation"],
        )
        mock_send_invite.assert_called_once()

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_resend_organization_invitation_unauthorized(self, mock_send_invite):
        invitation = OrganizationInvitation.objects.create(
            email="invitee@blsq.org",
            organization=self.organization,
            invited_by=self.owner,
            role=OrganizationMembershipRole.MEMBER,
        )

        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation ResendOrganizationInvitation($input: ResendOrganizationInvitationInput!) {
                resendOrganizationInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(invitation.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["resendOrganizationInvitation"],
        )
        mock_send_invite.assert_not_called()

    def test_organization_invitations_query(self):
        OrganizationInvitation.objects.create(
            email="invitee1@blsq.org",
            organization=self.organization,
            invited_by=self.owner,
            role=OrganizationMembershipRole.MEMBER,
        )
        OrganizationInvitation.objects.create(
            email="invitee2@blsq.org",
            organization=self.organization,
            invited_by=self.owner,
            role=OrganizationMembershipRole.ADMIN,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            query OrganizationInvitations($organizationId: UUID!) {
                organization(id: $organizationId) {
                    invitations {
                        items {
                            id
                            email
                            role
                            status
                        }
                    }
                }
            }
            """,
            {"organizationId": str(self.organization.id)},
        )

        invitation_emails = {
            inv["email"] for inv in r["data"]["organization"]["invitations"]["items"]
        }
        expected_emails = {"invitee1@blsq.org", "invitee2@blsq.org"}
        self.assertEqual(invitation_emails, expected_emails)
