from unittest.mock import patch

from django.core.signing import Signer
from django.test import TestCase

from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.authentication import (
    IdentityToken,
    MembershipToken,
    WorkspaceToken,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WorkspaceTokenAuthenticationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORG = Organization.objects.create(name="Auth Org")
        cls.MEMBER = User.objects.create_user("member@openhexa.org", "password")
        cls.ORG_ADMIN = User.objects.create_user("orgadmin@openhexa.org", "password")
        cls.OUTSIDER = User.objects.create_user("outsider@openhexa.org", "password")
        OrganizationMembership.objects.create(
            organization=cls.ORG,
            user=cls.ORG_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.ORG_ADMIN,
                name="Auth Workspace",
                organization=cls.ORG,
            )
        WorkspaceMembership.objects.filter(
            workspace=cls.WORKSPACE, user=cls.ORG_ADMIN
        ).delete()
        cls.MEMBERSHIP = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.MEMBER,
            role=WorkspaceMembershipRole.EDITOR,
        )

    def test_issue_returns_membership_token_for_members(self):
        token = WorkspaceToken.issue(
            user=self.MEMBER, workspace=self.WORKSPACE, membership=self.MEMBERSHIP
        )
        self.assertIsInstance(token, MembershipToken)

    def test_issue_returns_identity_token_without_membership(self):
        token = WorkspaceToken.issue(
            user=self.ORG_ADMIN, workspace=self.WORKSPACE, membership=None
        )
        self.assertIsInstance(token, IdentityToken)

    def test_membership_token_round_trip(self):
        signed = WorkspaceToken.issue(
            user=self.MEMBER, workspace=self.WORKSPACE, membership=self.MEMBERSHIP
        ).sign()
        self.assertEqual(
            Signer().unsign_object(signed), str(self.MEMBERSHIP.access_token)
        )
        token = WorkspaceToken.authenticate(signed)
        self.assertEqual((token.user, token.workspace), (self.MEMBER, self.WORKSPACE))

    def test_identity_token_round_trip(self):
        signed = WorkspaceToken.issue(
            user=self.ORG_ADMIN, workspace=self.WORKSPACE, membership=None
        ).sign()
        self.assertEqual(
            Signer().unsign_object(signed),
            {
                "type": "identity",
                "workspace_id": str(self.WORKSPACE.id),
                "user_id": str(self.ORG_ADMIN.id),
            },
        )
        token = WorkspaceToken.authenticate(signed)
        self.assertEqual(
            (token.user, token.workspace), (self.ORG_ADMIN, self.WORKSPACE)
        )

    def test_identity_token_rejected_when_access_revoked(self):
        signed = WorkspaceToken.issue(
            user=self.ORG_ADMIN, workspace=self.WORKSPACE, membership=None
        ).sign()
        OrganizationMembership.objects.filter(
            organization=self.ORG, user=self.ORG_ADMIN
        ).delete()
        self.assertIsNone(WorkspaceToken.authenticate(signed))

    def test_identity_token_rejected_for_deleted_user(self):
        signed = WorkspaceToken.issue(
            user=self.OUTSIDER, workspace=self.WORKSPACE, membership=None
        ).sign()
        self.OUTSIDER.delete()
        self.assertIsNone(WorkspaceToken.authenticate(signed))

    def test_tampered_token_rejected(self):
        signed = WorkspaceToken.issue(
            user=self.MEMBER, workspace=self.WORKSPACE, membership=self.MEMBERSHIP
        ).sign()
        self.assertIsNone(WorkspaceToken.authenticate(signed + "tampered"))
        self.assertIsNone(WorkspaceToken.authenticate("not-a-token"))

    def test_unknown_membership_token_rejected(self):
        self.assertIsNone(
            WorkspaceToken.authenticate(Signer().sign_object("does-not-exist"))
        )

    def test_unknown_payload_format_rejected(self):
        self.assertIsNone(
            WorkspaceToken.authenticate(
                Signer().sign_object({"type": "not-a-token-type"})
            )
        )
        self.assertIsNone(WorkspaceToken.authenticate(Signer().sign_object([1, 2])))
