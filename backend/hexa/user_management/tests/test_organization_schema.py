import base64
import uuid
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import (
    Organization,
    OrganizationInvitation,
    OrganizationInvitationStatus,
    OrganizationMembership,
    OrganizationMembershipRole,
    OrganizationSubscription,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


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


def _create_test_image():
    """Create a minimal valid PNG image as a data URL."""
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    )
    return f"data:image/png;base64,{base64.b64encode(png_bytes).decode()}"


class OrganizationUpdateDeleteTest(GraphQLTestCase, OrganizationTestMixin):
    def setUp(self):
        super().setUp()
        self.owner = self.create_user("owner@blsq.org")
        self.admin = self.create_user("admin@blsq.org")
        self.member = self.create_user("member@blsq.org")
        self.non_member = self.create_user("non_member@blsq.org")

        self.organization = self.create_organization(
            self.owner, "Test Organization", "Description", short_name="TEST"
        )
        self.join_organization(
            self.admin, self.organization, OrganizationMembershipRole.ADMIN
        )
        self.join_organization(
            self.member, self.organization, OrganizationMembershipRole.MEMBER
        )

        self.valid_logo = _create_test_image()

    def test_update_organization_name_success(self):
        """Test successful organization name update by owner."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                        name
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "name": "Updated Organization Name",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "organization": {
                    "id": str(self.organization.id),
                    "name": "Updated Organization Name",
                },
            },
            r["data"]["updateOrganization"],
        )

        self.organization.refresh_from_db()
        self.assertEqual(self.organization.name, "Updated Organization Name")

    def test_update_organization_short_name_success(self):
        """Test successful organization short name update."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                        shortName
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "shortName": "WHO",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "organization": {
                    "id": str(self.organization.id),
                    "shortName": "WHO",
                },
            },
            r["data"]["updateOrganization"],
        )

        self.organization.refresh_from_db()
        self.assertEqual(self.organization.short_name, "WHO")

    def test_update_organization_logo_success(self):
        """Test successful organization logo update."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                        logo
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "logo": self.valid_logo,
                }
            },
        )

        self.assertTrue(r["data"]["updateOrganization"]["success"])
        self.assertEqual(r["data"]["updateOrganization"]["errors"], [])
        self.assertIsNotNone(r["data"]["updateOrganization"]["organization"]["logo"])
        self.assertTrue(
            r["data"]["updateOrganization"]["organization"]["logo"].startswith(
                "data:image"
            )
        )

        self.organization.refresh_from_db()
        self.assertIsNotNone(self.organization.logo)

    def test_update_organization_remove_logo(self):
        """Test removing organization logo by sending empty string."""
        self.organization.logo = base64.b64decode(self.valid_logo.split(",")[1])
        self.organization.save()

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                        logo
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "logo": "",
                }
            },
        )

        self.assertTrue(r["data"]["updateOrganization"]["success"])
        self.assertEqual(r["data"]["updateOrganization"]["errors"], [])
        self.assertIsNone(r["data"]["updateOrganization"]["organization"]["logo"])

        self.organization.refresh_from_db()
        self.assertFalse(self.organization.logo)

    def test_update_organization_invalid_logo(self):
        """Test organization update with invalid logo format."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "logo": "not-a-valid-image-data-url",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["INVALID_LOGO"],
                "organization": None,
            },
            r["data"]["updateOrganization"],
        )

    def test_update_organization_name_duplicate(self):
        """Test organization update with duplicate name."""
        other_org = self.create_organization(
            self.owner, "Other Organization", "Other Description", short_name="OTHR"
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "name": other_org.name,
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["NAME_DUPLICATE"],
                "organization": None,
            },
            r["data"]["updateOrganization"],
        )

    def test_update_organization_short_name_duplicate(self):
        """Test organization update with duplicate short name."""
        other_org = self.create_organization(
            self.owner, "Other Organization", "Other Description", short_name="WHO"
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "shortName": other_org.short_name,
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["SHORT_NAME_DUPLICATE"],
                "organization": None,
            },
            r["data"]["updateOrganization"],
        )

    def test_update_organization_invalid_short_name_too_long(self):
        """Test organization update with short name that's too long."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "shortName": "TOOLONG",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["INVALID_SHORT_NAME"],
                "organization": None,
            },
            r["data"]["updateOrganization"],
        )

    def test_update_organization_invalid_short_name_lowercase(self):
        """Test organization update with lowercase short name."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "shortName": "who",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["INVALID_SHORT_NAME"],
                "organization": None,
            },
            r["data"]["updateOrganization"],
        )

    def test_update_organization_by_admin_success(self):
        """Test that admin can also update organization."""
        self.client.force_login(self.admin)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                        name
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "name": "Updated by Admin",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "organization": {
                    "id": str(self.organization.id),
                    "name": "Updated by Admin",
                },
            },
            r["data"]["updateOrganization"],
        )

    def test_update_organization_permission_denied_member(self):
        """Test that regular member cannot update organization."""
        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "name": "Unauthorized Update",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "organization": None,
            },
            r["data"]["updateOrganization"],
        )

    def test_update_organization_permission_denied_non_member(self):
        """Test that non-member cannot update organization"""
        self.client.force_login(self.non_member)
        r = self.run_query(
            """
            mutation UpdateOrganization($input: UpdateOrganizationInput!) {
                updateOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.organization.id),
                    "name": "Unauthorized Update",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["NOT_FOUND"],
                "organization": None,
            },
            r["data"]["updateOrganization"],
        )

    def test_delete_organization_success(self):
        """Test successful organization deletion by owner (soft delete)."""
        org_to_delete = self.create_organization(
            self.owner, "Organization to Delete", "Description", short_name="DEL1"
        )

        workspace1 = self.create_workspace(
            self.owner, org_to_delete, "Workspace 1", "Description 1"
        )
        workspace2 = self.create_workspace(
            self.owner, org_to_delete, "Workspace 2", "Description 2"
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation DeleteOrganization($input: DeleteOrganizationInput!) {
                deleteOrganization(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(org_to_delete.id),
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteOrganization"],
        )

        # Soft delete - organization still exists but is marked as deleted
        org_to_delete.refresh_from_db()
        self.assertIsNotNone(org_to_delete.deleted_at)

        workspace1.refresh_from_db()
        workspace2.refresh_from_db()
        self.assertTrue(workspace1.archived)
        self.assertTrue(workspace2.archived)

    def test_delete_organization_permission_denied_member(self):
        """Test that regular member cannot delete organization."""
        org_to_delete = self.create_organization(
            self.owner, "Organization to Delete 2", "Description", short_name="DEL2"
        )
        self.join_organization(
            self.member, org_to_delete, OrganizationMembershipRole.MEMBER
        )

        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation DeleteOrganization($input: DeleteOrganizationInput!) {
                deleteOrganization(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(org_to_delete.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteOrganization"],
        )

        self.assertTrue(Organization.objects.filter(id=org_to_delete.id).exists())

    def test_delete_organization_permission_denied_non_member(self):
        """Test that non-member cannot delete organization"""
        org_to_delete = self.create_organization(
            self.owner, "Organization to Delete 3", "Description", short_name="DEL3"
        )

        self.client.force_login(self.non_member)
        r = self.run_query(
            """
            mutation DeleteOrganization($input: DeleteOrganizationInput!) {
                deleteOrganization(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(org_to_delete.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["NOT_FOUND"]},
            r["data"]["deleteOrganization"],
        )

        self.assertTrue(Organization.objects.filter(id=org_to_delete.id).exists())


class CreateOrganizationTest(GraphQLTestCase, OrganizationTestMixin):
    """Tests for the createOrganization mutation (SaaS provisioning)."""

    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_superuser(
            email="superuser@blsq.org", password="Pa$$w0rd"
        )
        self.regular_user = self.create_user("regular@blsq.org")

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_create_organization_success(self, mock_send_invite):
        """Test superuser can create organization with new user (invitation flow)."""
        self.client.force_login(self.superuser)
        r = self.run_query(
            """
            mutation CreateOrganization($input: CreateOrganizationInput!) {
                createOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                        name
                    }
                    user {
                        email
                    }
                }
            }
            """,
            {
                "input": {
                    "ownerEmail": "newowner@example.org",
                    "name": "New SaaS Organization",
                    "subscriptionId": "12345678-1234-1234-1234-123456789012",
                    "planCode": "openhexa_starter",
                    "subscriptionStartDate": "2026-01-01",
                    "subscriptionEndDate": "2026-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertTrue(r["data"]["createOrganization"]["success"])
        self.assertEqual(r["data"]["createOrganization"]["errors"], [])
        self.assertEqual(
            r["data"]["createOrganization"]["organization"]["name"],
            "New SaaS Organization",
        )
        self.assertIsNone(r["data"]["createOrganization"]["user"])
        org = Organization.objects.get(name="New SaaS Organization")
        subscription = org.active_subscription
        self.assertIsNotNone(subscription)
        self.assertEqual(
            subscription.subscription_id,
            uuid.UUID("12345678-1234-1234-1234-123456789012"),
        )
        self.assertEqual(subscription.plan_code, "openhexa_starter")
        self.assertEqual(subscription.users_limit, 10)
        self.assertEqual(subscription.workspaces_limit, 5)
        self.assertEqual(subscription.pipeline_runs_limit, 1000)
        self.assertEqual(subscription.start_date, date(2026, 1, 1))
        self.assertEqual(subscription.end_date, date(2026, 12, 31))

        invitation = OrganizationInvitation.objects.get(
            organization=org,
            email="newowner@example.org",
        )
        self.assertEqual(invitation.role, OrganizationMembershipRole.OWNER)
        mock_send_invite.assert_called_once_with(invitation)

    @patch("hexa.user_management.schema.send_organization_add_user_email")
    def test_create_organization_with_existing_user(self, mock_send_email):
        """Test creating organization with an existing user as owner."""
        self.client.force_login(self.superuser)
        r = self.run_query(
            """
            mutation CreateOrganization($input: CreateOrganizationInput!) {
                createOrganization(input: $input) {
                    success
                    errors
                    user {
                        email
                    }
                }
            }
            """,
            {
                "input": {
                    "ownerEmail": self.regular_user.email,
                    "name": "Org for Existing User",
                    "subscriptionId": "22222222-2222-2222-2222-222222222222",
                    "planCode": "openhexa_starter",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2025-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertTrue(r["data"]["createOrganization"]["success"])
        self.assertEqual(
            r["data"]["createOrganization"]["user"]["email"], self.regular_user.email
        )

        self.assertEqual(User.objects.filter(email=self.regular_user.email).count(), 1)

        org = Organization.objects.get(name="Org for Existing User")
        self.assertTrue(self.regular_user.is_organization_owner(org))
        mock_send_email.assert_called_once()

    def test_create_organization_permission_denied(self):
        """Test user cannot create organization."""
        self.client.force_login(self.regular_user)
        r = self.run_query(
            """
            mutation CreateOrganization($input: CreateOrganizationInput!) {
                createOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "ownerEmail": "test@example.org",
                    "name": "Unauthorized Org",
                    "subscriptionId": "33333333-3333-3333-3333-333333333333",
                    "planCode": "openhexa_starter",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2025-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "organization": None,
            },
            r["data"]["createOrganization"],
        )

    def test_create_organization_duplicate_name(self):
        """Test that duplicate organization name is rejected."""
        Organization.objects.create(
            name="Existing Organization",
            organization_type="CORPORATE",
        )

        self.client.force_login(self.superuser)
        r = self.run_query(
            """
            mutation CreateOrganization($input: CreateOrganizationInput!) {
                createOrganization(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "ownerEmail": "test@example.org",
                    "name": "Existing Organization",
                    "subscriptionId": "44444444-4444-4444-4444-444444444444",
                    "planCode": "openhexa_starter",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2025-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["NAME_DUPLICATE"],
                "organization": None,
            },
            r["data"]["createOrganization"],
        )

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_create_organization_with_service_account_permission(
        self, mock_send_invite
    ):
        """Test that a non-superuser with manage_all_organizations permission can create organization."""
        service_account = self.create_user("service@console.blsq.org")
        content_type = ContentType.objects.get_for_model(Organization)
        permission = Permission.objects.get(
            codename="manage_all_organizations",
            content_type=content_type,
        )
        service_account.user_permissions.add(permission)

        self.client.force_login(service_account)
        r = self.run_query(
            """
            mutation CreateOrganization($input: CreateOrganizationInput!) {
                createOrganization(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "ownerEmail": "newowner@serviceaccount.org",
                    "name": "Service Account Created Org",
                    "subscriptionId": "66666666-6666-6666-6666-666666666666",
                    "planCode": "openhexa_starter",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2025-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertTrue(r["data"]["createOrganization"]["success"])
        self.assertEqual(r["data"]["createOrganization"]["errors"], [])


class UpdateOrganizationSubscriptionTest(GraphQLTestCase, OrganizationTestMixin):
    """Tests for the updateOrganizationSubscription mutation."""

    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_superuser(
            email="superuser@blsq.org", password="Pa$$w0rd"
        )
        self.regular_user = self.create_user("regular@blsq.org")
        self.owner = self.create_user("owner@blsq.org")

        # Create organization with subscription
        self.organization = Organization.objects.create(
            name="Test Organization",
            organization_type="CORPORATE",
            short_name="TORG",
        )
        OrganizationMembership.objects.create(
            organization=self.organization,
            user=self.owner,
            role=OrganizationMembershipRole.OWNER,
        )
        self.subscription = OrganizationSubscription.objects.create(
            organization=self.organization,
            subscription_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            plan_code="openhexa_starter",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            users_limit=10,
            workspaces_limit=5,
            pipeline_runs_limit=1000,
        )

        # Create organization without subscription
        self.org_no_subscription = Organization.objects.create(
            name="No Subscription Org",
            organization_type="CORPORATE",
            short_name="NOSUB",
        )

    def test_update_subscription_success(self):
        """Test superuser can update organization subscription."""
        self.client.force_login(self.superuser)
        r = self.run_query(
            """
            mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
                updateOrganizationSubscription(input: $input) {
                    success
                    errors
                    organization {
                        id
                        name
                    }
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.organization.id),
                    "subscriptionId": str(self.subscription.subscription_id),
                    "planCode": "openhexa_pro",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2026-12-31",
                    "limits": {
                        "users": 50,
                        "workspaces": 20,
                        "pipelineRuns": 10000,
                    },
                }
            },
        )

        self.assertTrue(r["data"]["updateOrganizationSubscription"]["success"])
        self.assertEqual(r["data"]["updateOrganizationSubscription"]["errors"], [])

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.plan_code, "openhexa_pro")
        self.assertEqual(self.subscription.users_limit, 50)
        self.assertEqual(self.subscription.workspaces_limit, 20)
        self.assertEqual(self.subscription.pipeline_runs_limit, 10000)
        self.assertEqual(self.subscription.end_date, date(2026, 12, 31))

    def test_update_subscription_creates_new_for_new_subscription_id(self):
        """Test that using a new subscriptionId creates a new subscription (for downgrades/renewals)."""
        self.client.force_login(self.superuser)
        new_subscription_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        r = self.run_query(
            """
            mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
                updateOrganizationSubscription(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.organization.id),
                    "subscriptionId": new_subscription_id,
                    "planCode": "openhexa_enterprise",
                    "subscriptionStartDate": "2026-01-01",
                    "subscriptionEndDate": "2026-12-31",
                    "limits": {
                        "users": 100,
                        "workspaces": 50,
                        "pipelineRuns": 50000,
                    },
                }
            },
        )

        self.assertTrue(r["data"]["updateOrganizationSubscription"]["success"])

        # Verify new subscription was created
        new_sub = OrganizationSubscription.objects.get(
            subscription_id=uuid.UUID(new_subscription_id)
        )
        self.assertEqual(new_sub.organization, self.organization)
        self.assertEqual(new_sub.plan_code, "openhexa_enterprise")
        self.assertEqual(new_sub.users_limit, 100)

        # Original subscription should still exist
        self.assertTrue(
            OrganizationSubscription.objects.filter(
                subscription_id=self.subscription.subscription_id
            ).exists()
        )

    def test_update_subscription_permission_denied(self):
        """Test that non-superuser cannot update subscription."""
        self.client.force_login(self.regular_user)
        r = self.run_query(
            """
            mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
                updateOrganizationSubscription(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.organization.id),
                    "subscriptionId": str(self.subscription.subscription_id),
                    "planCode": "openhexa_pro",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2025-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "organization": None,
            },
            r["data"]["updateOrganizationSubscription"],
        )

    def test_update_subscription_not_found(self):
        """Test updating subscription for non-existent organization."""
        self.client.force_login(self.superuser)
        r = self.run_query(
            """
            mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
                updateOrganizationSubscription(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "organizationId": "00000000-0000-0000-0000-000000000000",
                    "subscriptionId": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                    "planCode": "openhexa_pro",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2025-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["NOT_FOUND"],
                "organization": None,
            },
            r["data"]["updateOrganizationSubscription"],
        )

    def test_update_subscription_creates_for_org_without_subscription(self):
        """Test that mutation creates subscription for organization without one."""
        self.client.force_login(self.superuser)
        new_subscription_id = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
        r = self.run_query(
            """
            mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
                updateOrganizationSubscription(input: $input) {
                    success
                    errors
                    organization {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.org_no_subscription.id),
                    "subscriptionId": new_subscription_id,
                    "planCode": "openhexa_pro",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2025-12-31",
                    "limits": {
                        "users": 10,
                        "workspaces": 5,
                        "pipelineRuns": 1000,
                    },
                }
            },
        )

        self.assertTrue(r["data"]["updateOrganizationSubscription"]["success"])

        subscription = OrganizationSubscription.objects.get(
            subscription_id=uuid.UUID(new_subscription_id)
        )
        self.assertEqual(subscription.organization, self.org_no_subscription)
        self.assertEqual(subscription.plan_code, "openhexa_pro")

    def test_update_subscription_with_service_account_permission(self):
        """Test that a non-superuser with manage_all_organizations permission can update subscription."""
        service_account = self.create_user("service@console.blsq.org")
        content_type = ContentType.objects.get_for_model(Organization)
        permission = Permission.objects.get(
            codename="manage_all_organizations",
            content_type=content_type,
        )
        service_account.user_permissions.add(permission)

        self.client.force_login(service_account)
        r = self.run_query(
            """
            mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
                updateOrganizationSubscription(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "organizationId": str(self.organization.id),
                    "subscriptionId": str(self.subscription.subscription_id),
                    "planCode": "openhexa_enterprise",
                    "subscriptionStartDate": "2025-01-01",
                    "subscriptionEndDate": "2027-12-31",
                    "limits": {
                        "users": 100,
                        "workspaces": 50,
                        "pipelineRuns": 50000,
                    },
                }
            },
        )

        self.assertTrue(r["data"]["updateOrganizationSubscription"]["success"])
        self.assertEqual(r["data"]["updateOrganizationSubscription"]["errors"], [])


class OrganizationUsageLimitsTest(GraphQLTestCase, OrganizationTestMixin):
    """Tests for the usage and limits resolvers on Organization type."""

    def setUp(self):
        super().setUp()
        self.owner = self.create_user("owner@blsq.org")
        self.member = self.create_user("member@blsq.org")

        self.organization = self.create_organization(
            self.owner, "Test Organization", "Description"
        )
        self.join_organization(
            self.member, self.organization, OrganizationMembershipRole.MEMBER
        )

    def test_organization_usage_self_hosted(self):
        """Test usage and subscription for self-hosted (no subscription)."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            query OrganizationUsage($organizationId: UUID!) {
                organization(id: $organizationId) {
                    usage {
                        users
                        workspaces
                        pipelineRuns
                    }
                    subscription {
                        subscriptionId
                        planCode
                        startDate
                        endDate
                        limits {
                            users
                            workspaces
                            pipelineRuns
                        }
                    }
                }
            }
            """,
            {"organizationId": str(self.organization.id)},
        )

        usage = r["data"]["organization"]["usage"]
        subscription = r["data"]["organization"]["subscription"]
        # Usage counts should be present
        self.assertEqual(usage["users"], 2)
        self.assertEqual(usage["workspaces"], 0)
        self.assertEqual(usage["pipelineRuns"], 0)
        self.assertIsNone(subscription)

    def test_organization_usage_and_subscription_saas(self):
        """Test usage and subscription with SaaS subscription details."""
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=335)
        OrganizationSubscription.objects.create(
            organization=self.organization,
            subscription_id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            plan_code="openhexa_starter",
            start_date=start_date,
            end_date=end_date,
            users_limit=10,
            workspaces_limit=5,
            pipeline_runs_limit=1000,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            query OrganizationUsageSubscription($organizationId: UUID!) {
                organization(id: $organizationId) {
                    usage {
                        users
                        workspaces
                        pipelineRuns
                    }
                    subscription {
                        subscriptionId
                        planCode
                        startDate
                        endDate
                        limits {
                            users
                            workspaces
                            pipelineRuns
                        }
                    }
                }
            }
            """,
            {"organizationId": str(self.organization.id)},
        )

        usage = r["data"]["organization"]["usage"]
        subscription = r["data"]["organization"]["subscription"]
        self.assertEqual(usage["users"], 2)
        self.assertEqual(usage["workspaces"], 0)
        self.assertEqual(usage["pipelineRuns"], 0)
        self.assertEqual(
            subscription["subscriptionId"],
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        )
        self.assertEqual(subscription["planCode"], "openhexa_starter")
        self.assertEqual(subscription["startDate"], start_date.isoformat())
        self.assertEqual(subscription["endDate"], end_date.isoformat())
        self.assertEqual(subscription["limits"]["users"], 10)
        self.assertEqual(subscription["limits"]["workspaces"], 5)
        self.assertEqual(subscription["limits"]["pipelineRuns"], 1000)


class SubscriptionLimitEnforcementTest(GraphQLTestCase, OrganizationTestMixin):
    """Tests for subscription limit enforcement."""

    def setUp(self):
        super().setUp()
        self.owner = self.create_user("owner@blsq.org")
        self.organization = self.create_organization(
            self.owner, "Test Organization", "Description", short_name="SLIM"
        )

        today = timezone.now().date()
        self.subscription = OrganizationSubscription.objects.create(
            organization=self.organization,
            subscription_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            plan_code="openhexa_starter",
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=335),
            users_limit=2,
            workspaces_limit=1,
            pipeline_runs_limit=5,
        )

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_invite_member_at_user_limit(self, mock_send_invite):
        """Test that inviting a member when at user limit returns error."""
        member = self.create_user("member@blsq.org")
        self.join_organization(
            member, self.organization, OrganizationMembershipRole.MEMBER
        )

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
                    "userEmail": "newuser@blsq.org",
                    "organizationRole": "MEMBER",
                    "workspaceInvitations": [],
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["USERS_LIMIT_REACHED"]},
            r["data"]["inviteOrganizationMember"],
        )
        mock_send_invite.assert_not_called()

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_invite_member_under_user_limit(self, mock_send_invite):
        """Test that inviting a member when under limit succeeds."""
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
                    "userEmail": "newuser@blsq.org",
                    "organizationRole": "MEMBER",
                    "workspaceInvitations": [],
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["inviteOrganizationMember"],
        )
        mock_send_invite.assert_called_once()

    @patch("hexa.user_management.schema.send_organization_invite")
    def test_invite_member_no_subscription(self, mock_send_invite):
        """Test that inviting works without subscription (self-hosted mode)."""
        owner2 = self.create_user("owner2@blsq.org")
        org_no_sub = self.create_organization(
            owner2, "No Sub Org", "Description", short_name="NSUB"
        )

        self.client.force_login(owner2)
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
                    "organizationId": str(org_no_sub.id),
                    "userEmail": "newuser@blsq.org",
                    "organizationRole": "MEMBER",
                    "workspaceInvitations": [],
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["inviteOrganizationMember"],
        )
        mock_send_invite.assert_called_once()

    def test_active_subscription_date_based(self):
        """Test that limits only apply to active subscriptions based on date."""
        today = timezone.now().date()
        future_subscription = OrganizationSubscription.objects.create(
            organization=self.organization,
            subscription_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            plan_code="openhexa_pro",
            start_date=today + timedelta(days=365),
            end_date=today + timedelta(days=730),
            users_limit=100,  # Higher limit
            workspaces_limit=50,
            pipeline_runs_limit=10000,
        )

        self.assertEqual(
            self.organization.active_subscription.subscription_id,
            self.subscription.subscription_id,
        )

        self.assertEqual(
            self.organization.upcoming_subscription.subscription_id,
            future_subscription.subscription_id,
        )

    def test_is_users_limit_reached_method(self):
        """Test the is_users_limit_reached helper method."""
        self.assertFalse(self.organization.is_users_limit_reached())

        member = self.create_user("member2@blsq.org")
        self.join_organization(
            member, self.organization, OrganizationMembershipRole.MEMBER
        )

        self.assertTrue(self.organization.is_users_limit_reached())

    def test_is_workspaces_limit_reached_method(self):
        """Test the is_workspaces_limit_reached helper method."""
        self.assertFalse(self.organization.is_workspaces_limit_reached())

        self.create_workspace(
            self.owner, self.organization, "Test Workspace", "Description"
        )
        self.assertTrue(self.organization.is_workspaces_limit_reached())


class ExternalCollaboratorTest(GraphQLTestCase, OrganizationTestMixin):
    """Tests for external collaborators - users with workspace access but no organization membership."""

    def setUp(self):
        super().setUp()
        self.owner = self.create_user("owner@blsq.org")
        self.admin = self.create_user("admin@blsq.org")
        self.member = self.create_user("member@blsq.org")
        self.external_collaborator = self.create_user("external@blsq.org")
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

        # Create workspaces
        self.workspace1 = self.create_workspace(
            self.owner, self.organization, "Workspace 1", "Description 1"
        )
        self.workspace2 = self.create_workspace(
            self.owner, self.organization, "Workspace 2", "Description 2"
        )

        # Add external collaborator to workspace (no organization membership)
        self.external_workspace_membership = WorkspaceMembership.objects.create(
            user=self.external_collaborator,
            workspace=self.workspace1,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_external_collaborators_query(self):
        """Test that external collaborators are returned correctly."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            query ExternalCollaborators($organizationId: UUID!) {
                organization(id: $organizationId) {
                    externalCollaborators {
                        totalItems
                        items {
                            id
                            user {
                                email
                            }
                            workspaceMemberships {
                                workspace {
                                    slug
                                }
                                role
                            }
                        }
                    }
                }
            }
            """,
            {"organizationId": str(self.organization.id)},
        )

        external_collaborators = r["data"]["organization"]["externalCollaborators"]
        self.assertEqual(external_collaborators["totalItems"], 1)
        self.assertEqual(len(external_collaborators["items"]), 1)
        self.assertEqual(
            external_collaborators["items"][0]["user"]["email"], "external@blsq.org"
        )
        self.assertEqual(
            external_collaborators["items"][0]["workspaceMemberships"][0]["workspace"][
                "slug"
            ],
            self.workspace1.slug,
        )

    def test_external_collaborators_query_excludes_org_members(self):
        """Test that organization members are not returned as external collaborators."""
        # Add organization member to workspace
        WorkspaceMembership.objects.create(
            user=self.member,
            workspace=self.workspace1,
            role=WorkspaceMembershipRole.EDITOR,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            query ExternalCollaborators($organizationId: UUID!) {
                organization(id: $organizationId) {
                    externalCollaborators {
                        totalItems
                        items {
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

        external_collaborators = r["data"]["organization"]["externalCollaborators"]
        emails = {item["user"]["email"] for item in external_collaborators["items"]}
        self.assertIn("external@blsq.org", emails)
        self.assertNotIn("member@blsq.org", emails)

    def test_external_collaborators_query_empty_for_regular_member(self):
        """Test that regular members cannot see external collaborators list."""
        self.client.force_login(self.member)
        r = self.run_query(
            """
            query ExternalCollaborators($organizationId: UUID!) {
                organization(id: $organizationId) {
                    externalCollaborators {
                        totalItems
                        items {
                            id
                        }
                    }
                }
            }
            """,
            {"organizationId": str(self.organization.id)},
        )

        external_collaborators = r["data"]["organization"]["externalCollaborators"]
        self.assertEqual(external_collaborators["totalItems"], 0)
        self.assertEqual(len(external_collaborators["items"]), 0)

    def test_external_collaborators_query_with_search_term(self):
        """Test searching external collaborators by email/name."""
        # Add another external collaborator
        other_external = self.create_user("other_external@blsq.org")
        WorkspaceMembership.objects.create(
            user=other_external,
            workspace=self.workspace2,
            role=WorkspaceMembershipRole.VIEWER,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            query ExternalCollaborators($organizationId: UUID!, $term: String) {
                organization(id: $organizationId) {
                    externalCollaborators(term: $term) {
                        totalItems
                        items {
                            user {
                                email
                            }
                        }
                    }
                }
            }
            """,
            {"organizationId": str(self.organization.id), "term": "other"},
        )

        external_collaborators = r["data"]["organization"]["externalCollaborators"]
        self.assertEqual(external_collaborators["totalItems"], 1)
        self.assertEqual(
            external_collaborators["items"][0]["user"]["email"],
            "other_external@blsq.org",
        )

    def test_update_external_collaborator(self):
        """Test updating external collaborator workspace permissions."""
        # Verify initial state before update
        self.assertEqual(
            self.external_workspace_membership.role, WorkspaceMembershipRole.VIEWER
        )
        self.assertFalse(
            WorkspaceMembership.objects.filter(
                user=self.external_collaborator, workspace=self.workspace2
            ).exists()
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateExternalCollaborator($input: UpdateExternalCollaboratorInput!) {
                updateExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "workspacePermissions": [
                        {
                            "workspaceSlug": self.workspace1.slug,
                            "role": "EDITOR",
                        },
                        {
                            "workspaceSlug": self.workspace2.slug,
                            "role": "VIEWER",
                        },
                    ],
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["updateExternalCollaborator"],
        )

        # Verify workspace1 role was updated
        self.external_workspace_membership.refresh_from_db()
        self.assertEqual(
            self.external_workspace_membership.role, WorkspaceMembershipRole.EDITOR
        )

        # Verify workspace2 membership was created
        workspace2_membership = WorkspaceMembership.objects.get(
            user=self.external_collaborator, workspace=self.workspace2
        )
        self.assertEqual(workspace2_membership.role, WorkspaceMembershipRole.VIEWER)

    def test_update_external_collaborator_remove_from_workspace(self):
        """Test removing external collaborator from a workspace."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateExternalCollaborator($input: UpdateExternalCollaboratorInput!) {
                updateExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "workspacePermissions": [
                        {
                            "workspaceSlug": self.workspace1.slug,
                            "role": None,
                        },
                    ],
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["updateExternalCollaborator"],
        )

        # Verify membership was deleted
        self.assertFalse(
            WorkspaceMembership.objects.filter(
                user=self.external_collaborator, workspace=self.workspace1
            ).exists()
        )

    def test_update_external_collaborator_unauthorized(self):
        """Test that non-members cannot update external collaborators."""
        self.client.force_login(self.non_member)
        r = self.run_query(
            """
            mutation UpdateExternalCollaborator($input: UpdateExternalCollaboratorInput!) {
                updateExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "workspacePermissions": [],
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["ORGANIZATION_NOT_FOUND"]},
            r["data"]["updateExternalCollaborator"],
        )

    def test_update_external_collaborator_by_regular_member(self):
        """Test that regular members cannot update external collaborators."""
        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation UpdateExternalCollaborator($input: UpdateExternalCollaboratorInput!) {
                updateExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "workspacePermissions": [],
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["updateExternalCollaborator"],
        )

    def test_update_external_collaborator_by_admin(self):
        """Test that organization admins can update external collaborators."""
        self.client.force_login(self.admin)
        r = self.run_query(
            """
            mutation UpdateExternalCollaborator($input: UpdateExternalCollaboratorInput!) {
                updateExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "workspacePermissions": [
                        {
                            "workspaceSlug": self.workspace1.slug,
                            "role": "ADMIN",
                        },
                    ],
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["updateExternalCollaborator"],
        )

    def test_update_external_collaborator_user_not_found(self):
        """Test updating a non-existent user."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation UpdateExternalCollaborator($input: UpdateExternalCollaboratorInput!) {
                updateExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": "00000000-0000-0000-0000-000000000000",
                    "organizationId": str(self.organization.id),
                    "workspacePermissions": [],
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["USER_NOT_FOUND"]},
            r["data"]["updateExternalCollaborator"],
        )

    def test_delete_external_collaborator(self):
        """Test deleting an external collaborator removes all workspace memberships."""
        # Add external collaborator to second workspace
        WorkspaceMembership.objects.create(
            user=self.external_collaborator,
            workspace=self.workspace2,
            role=WorkspaceMembershipRole.EDITOR,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation DeleteExternalCollaborator($input: DeleteExternalCollaboratorInput!) {
                deleteExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteExternalCollaborator"],
        )

        # Verify all workspace memberships within the organization are deleted
        self.assertFalse(
            WorkspaceMembership.objects.filter(
                user=self.external_collaborator,
                workspace__organization=self.organization,
            ).exists()
        )

    def test_delete_external_collaborator_unauthorized(self):
        """Test that non-members cannot delete external collaborators."""
        self.client.force_login(self.non_member)
        r = self.run_query(
            """
            mutation DeleteExternalCollaborator($input: DeleteExternalCollaboratorInput!) {
                deleteExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["ORGANIZATION_NOT_FOUND"]},
            r["data"]["deleteExternalCollaborator"],
        )

        # Verify membership still exists
        self.assertTrue(
            WorkspaceMembership.objects.filter(
                id=self.external_workspace_membership.id
            ).exists()
        )

    def test_delete_external_collaborator_by_regular_member(self):
        """Test that regular members cannot delete external collaborators."""
        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation DeleteExternalCollaborator($input: DeleteExternalCollaboratorInput!) {
                deleteExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteExternalCollaborator"],
        )

    def test_delete_external_collaborator_by_admin(self):
        """Test that organization admins can delete external collaborators."""
        # Add external collaborator to second workspace
        WorkspaceMembership.objects.create(
            user=self.external_collaborator,
            workspace=self.workspace2,
            role=WorkspaceMembershipRole.EDITOR,
        )

        # Verify memberships exist before deletion
        self.assertEqual(
            WorkspaceMembership.objects.filter(
                user=self.external_collaborator,
                workspace__organization=self.organization,
            ).count(),
            2,
        )

        self.client.force_login(self.admin)
        r = self.run_query(
            """
            mutation DeleteExternalCollaborator($input: DeleteExternalCollaboratorInput!) {
                deleteExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteExternalCollaborator"],
        )

        # Verify all workspace memberships within the organization are deleted
        self.assertFalse(
            WorkspaceMembership.objects.filter(
                user=self.external_collaborator,
                workspace__organization=self.organization,
            ).exists()
        )

    def test_delete_external_collaborator_user_not_found(self):
        """Test deleting a non-existent user."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation DeleteExternalCollaborator($input: DeleteExternalCollaboratorInput!) {
                deleteExternalCollaborator(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": "00000000-0000-0000-0000-000000000000",
                    "organizationId": str(self.organization.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["USER_NOT_FOUND"]},
            r["data"]["deleteExternalCollaborator"],
        )

    def test_external_collaborator_can_view_organization(self):
        """Test that external collaborators can view the organization they have workspace access to."""
        self.client.force_login(self.external_collaborator)
        r = self.run_query(
            """
            query Organization($organizationId: UUID!) {
                organization(id: $organizationId) {
                    id
                    name
                }
            }
            """,
            {"organizationId": str(self.organization.id)},
        )

        self.assertIsNotNone(r["data"]["organization"])
        self.assertEqual(r["data"]["organization"]["name"], "Test Organization")

    def test_convert_external_collaborator_to_member(self):
        """Test converting an external collaborator to an organization member with MEMBER role."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                    membership {
                        id
                        role
                        user {
                            id
                            email
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "MEMBER",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertTrue(result["success"])
        self.assertEqual(result["errors"], [])
        self.assertIsNotNone(result["membership"])
        self.assertEqual(result["membership"]["role"], "MEMBER")
        self.assertEqual(result["membership"]["user"]["email"], "external@blsq.org")

        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=self.external_collaborator,
                organization=self.organization,
                role=OrganizationMembershipRole.MEMBER,
            ).exists()
        )

        self.assertTrue(
            WorkspaceMembership.objects.filter(
                user=self.external_collaborator, workspace=self.workspace1
            ).exists()
        )

    def test_convert_external_collaborator_to_admin(self):
        """Test converting an external collaborator to an organization admin."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                    membership {
                        role
                    }
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "ADMIN",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertTrue(result["success"])
        self.assertEqual(result["membership"]["role"], "ADMIN")

        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=self.external_collaborator,
                organization=self.organization,
                role=OrganizationMembershipRole.ADMIN,
            ).exists()
        )

    def test_convert_external_collaborator_to_owner(self):
        """Test converting an external collaborator to an organization owner."""
        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                    membership {
                        role
                    }
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "OWNER",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertTrue(result["success"])
        self.assertEqual(result["membership"]["role"], "OWNER")

        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=self.external_collaborator,
                organization=self.organization,
                role=OrganizationMembershipRole.OWNER,
            ).exists()
        )

    def test_convert_external_collaborator_to_owner_denied_for_admin(self):
        """Test that admins cannot convert external collaborators to owners."""
        self.client.force_login(self.admin)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "OWNER",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["PERMISSION_DENIED"])

        self.assertFalse(
            OrganizationMembership.objects.filter(
                user=self.external_collaborator,
                organization=self.organization,
            ).exists()
        )

    def test_convert_external_collaborator_already_member(self):
        """Test that converting a user who is already an org member fails."""
        OrganizationMembership.objects.create(
            user=self.external_collaborator,
            organization=self.organization,
            role=OrganizationMembershipRole.MEMBER,
        )

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "MEMBER",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["NOT_EXTERNAL_COLLABORATOR"])

    def test_convert_external_collaborator_no_workspace_membership(self):
        """Test that converting a user without workspace access fails."""
        self.external_workspace_membership.delete()

        self.client.force_login(self.owner)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "MEMBER",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["NOT_EXTERNAL_COLLABORATOR"])

    def test_convert_external_collaborator_unauthorized(self):
        """Test that non-members cannot convert external collaborators."""
        self.client.force_login(self.non_member)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "MEMBER",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["ORGANIZATION_NOT_FOUND"])

    def test_convert_external_collaborator_by_regular_member(self):
        """Test that regular members cannot convert external collaborators."""
        self.client.force_login(self.member)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "MEMBER",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertFalse(result["success"])
        self.assertEqual(result["errors"], ["PERMISSION_DENIED"])

    def test_convert_external_collaborator_by_admin(self):
        """Test that organization admins can convert external collaborators."""
        self.client.force_login(self.admin)
        r = self.run_query(
            """
            mutation ConvertExternalCollaboratorToMember($input: ConvertExternalCollaboratorToMemberInput!) {
                convertExternalCollaboratorToMember(input: $input) {
                    success
                    errors
                    membership {
                        role
                    }
                }
            }
            """,
            {
                "input": {
                    "userId": str(self.external_collaborator.id),
                    "organizationId": str(self.organization.id),
                    "role": "ADMIN",
                }
            },
        )

        result = r["data"]["convertExternalCollaboratorToMember"]
        self.assertTrue(result["success"])
        self.assertEqual(result["membership"]["role"], "ADMIN")
