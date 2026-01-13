import base64
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": "00000000-0000-0000-0000-000000000000",
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": str(self.external_collaborator.id),
                    "organization_id": str(self.organization.id),
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
                    "user_id": "00000000-0000-0000-0000-000000000000",
                    "organization_id": str(self.organization.id),
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
