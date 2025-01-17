import base64
import uuid
from unittest.mock import patch
from urllib.parse import urlencode

from django.conf import settings
from django.core import mail
from django.core.signing import Signer

from hexa.core.test import GraphQLTestCase
from hexa.databases.utils import TableNotFound
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WorkspaceTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_REBECCA = None
    USER_JULIA = None
    USER_WORKSPACE_ADMIN = None
    USER_EXTERNAL = None
    WORKSPACE = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )

        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_PENDING = User.objects.create_user(
            "pending@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword"
        )
        cls.USER_JOE = User.objects.create_user("joe@bluesquarehub.com", "joepassword")

        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces.prevent_create"),
            user=cls.USER_SABRINA,
        )

        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "workspaceroot@bluesquarehub.com",
            "workspace",
        )
        cls.USER_EXTERNAL = "user@external.com"

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_JULIA,
                name="Senegal Workspace",
                description="This is a workspace for Senegal",
                countries=[{"code": "AL"}],
            )
            cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
                cls.USER_JULIA,
                name="Burundi Workspace",
                description="This is a workspace for Burundi",
                countries=[{"code": "AD"}],
            )

        cls.WORKSPACE_MEMBERSHIP = WorkspaceMembership.objects.create(
            user=cls.USER_REBECCA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.WORKSPACE_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            user=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.INVITATION_FOO = WorkspaceInvitation.objects.create(
            invited_by=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            email=cls.USER_EXTERNAL,
            role=WorkspaceMembershipRole.VIEWER,
            status=WorkspaceInvitationStatus.PENDING,
        )
        cls.INVITATION_BAR = WorkspaceInvitation.objects.create(
            invited_by=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            email=cls.USER_REBECCA.email,
            role=WorkspaceMembershipRole.VIEWER,
            status=WorkspaceInvitationStatus.ACCEPTED,
        )
        cls.INVITATION_PENDING = WorkspaceInvitation.objects.create(
            invited_by=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE,
            email=cls.USER_PENDING.email,
            role=WorkspaceMembershipRole.VIEWER,
            status=WorkspaceInvitationStatus.PENDING,
        )
        cls.INVITATION_BAZ = WorkspaceInvitation.objects.create(
            invited_by=cls.USER_WORKSPACE_ADMIN,
            workspace=cls.WORKSPACE_2,
            email=cls.USER_REBECCA.email,
            role=WorkspaceMembershipRole.VIEWER,
            status=WorkspaceInvitationStatus.ACCEPTED,
        )

    def test_create_workspace_denied(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"], "workspace": None},
            r["data"]["createWorkspace"],
        )

    def test_create_workspace(self):
        self.client.force_login(self.USER_JOE)
        r = self.run_query(
            """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "workspace": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                },
                "errors": [],
            },
            r["data"]["createWorkspace"],
        )

    def test_create_workspace_prevent_create(self):
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces.prevent_create"),
            user=self.USER_JOE,
        )
        self.client.force_login(self.USER_JOE)
        r = self.run_query(
            """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "name": "Cameroon workspace",
                    "description": "Description",
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"], "workspace": None},
            r["data"]["createWorkspace"],
        )

    def test_create_workspace_with_demo_data(self):
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ) as mocked_load_database_sample, patch(
            "hexa.workspaces.models.load_bucket_sample_data"
        ) as mocked_load_bucket_sample:
            self.client.force_login(self.USER_JULIA)
            r = self.run_query(
                """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                        createdBy {
                          email
                        }
                    }
                    errors
                }
            }
            """,
                {
                    "input": {
                        "name": "Cameroon workspace",
                        "description": "Description",
                        "loadSampleData": True,
                    }
                },
            )
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "workspace": {
                        "name": "Cameroon workspace",
                        "description": "Description",
                        "createdBy": {"email": self.USER_JULIA.email},
                    },
                },
                r["data"]["createWorkspace"],
            )
            self.assertTrue(mocked_load_bucket_sample.called)
            self.assertTrue(mocked_load_database_sample.called)

    def test_create_workspace_without_demo_data(self):
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ) as mocked_load_database_sample, patch(
            "hexa.workspaces.models.load_bucket_sample_data"
        ) as mocked_load_bucket_sample:
            self.client.force_login(self.USER_JULIA)
            r = self.run_query(
                """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                        createdBy {
                          email
                        }
                    }
                    errors
                }
            }
            """,
                {
                    "input": {
                        "name": "Cameroon workspace",
                        "description": "Description",
                    }
                },
            )
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "workspace": {
                        "name": "Cameroon workspace",
                        "description": "Description",
                        "createdBy": {"email": self.USER_JULIA.email},
                    },
                },
                r["data"]["createWorkspace"],
            )
            self.assertFalse(mocked_load_bucket_sample.called)
            self.assertFalse(mocked_load_database_sample.called)

    def test_create_workspace_with_country(self):
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            self.client.force_login(self.USER_JULIA)
            r = self.run_query(
                """
            mutation createWorkspace($input:CreateWorkspaceInput!) {
                createWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                        countries {
                          code
                        }
                    }
                   
                    errors
                }
            }
            """,
                {
                    "input": {
                        "name": "Cameroon workspace",
                        "description": "Description",
                        "countries": [{"code": "AD"}],
                    }
                },
            )
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "workspace": {
                        "name": "Cameroon workspace",
                        "description": "Description",
                        "countries": [{"code": "AD"}],
                    },
                },
                r["data"]["createWorkspace"],
            )

    def test_get_workspace_not_member(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            query workspace($slug: String!) {
                workspace(slug: $slug) {
                    name
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )
        self.assertIsNone(
            r["data"]["workspace"],
        )

    def test_get_workspace(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            query workspace($slug: String!) {
                workspace(slug: $slug) {
                    name
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )
        self.assertEqual(
            {"name": self.WORKSPACE.name},
            r["data"]["workspace"],
        )

    def test_get_workspaces(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            query workspaces($page:Int!, $perPage:Int!) {
                workspaces(page:$page, perPage:$perPage) {
                   totalItems
                   totalPages
                   items {
                        slug
                        name
                   }
                }
            }
            """,
            {"page": 1, "perPage": 1},
        )

        self.assertEqual(
            {
                "totalItems": 1,
                "totalPages": 1,
                "items": [{"slug": self.WORKSPACE.slug, "name": self.WORKSPACE.name}],
            },
            r["data"]["workspaces"],
        )

    def test_update_workspace_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspace($input:UpdateWorkspaceInput!) {
                updateWorkspace(input: $input) {
                    success
                    workspace {
                        name
                        description
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": "c02704ff-541f-4519-8619-34da7acc010b",
                    "name": "Cameroon workspace",
                    "description": "Description",
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["NOT_FOUND"], "workspace": None},
            r["data"]["updateWorkspace"],
        )

    def test_update_workspace(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspace($input:UpdateWorkspaceInput!) {
                updateWorkspace(input: $input) {
                    success
                    workspace {
                        description
                        dockerImage
                    }
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                    "description": "This is a test for updating workspace description",
                    "dockerImage": "blsq/custom-image",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "workspace": {
                    "description": "This is a test for updating workspace description",
                    "dockerImage": "blsq/custom-image",
                },
            },
            r["data"]["updateWorkspace"],
        )

    def test_delete_workspace_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation deleteWorkspace($input: DeleteWorkspaceInput!) {
                deleteWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["NOT_FOUND"],
            },
            r["data"]["deleteWorkspace"],
        )

    # @patch("hexa.workspaces.models.delete_database")
    # def test_delete_workspace(self, mock_delete_database):
    def test_delete_workspace(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspace($input: DeleteWorkspaceInput!) {
                deleteWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                }
            },
        )
        # self.assertTrue(mock_delete_database.called)
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["deleteWorkspace"],
        )

    def test_archive_workspace_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation archiveWorkspace($input: ArchiveWorkspaceInput!) {
                archiveWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["NOT_FOUND"],
            },
            r["data"]["archiveWorkspace"],
        )

    def test_archive_workspace(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation archiveWorkspace($input: ArchiveWorkspaceInput!) {
                archiveWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "slug": self.WORKSPACE.slug,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["archiveWorkspace"],
        )

    def test_invite_workspace_member(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
                inviteWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        role
                        user {
                          email
                        }
                    }
                }
            }

            """,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "userEmail": self.USER_SABRINA.email,
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {"success": True, "errors": [], "workspaceMembership": None},
            r["data"]["inviteWorkspaceMember"],
        )

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(
            f"You've been added to the workspace {self.WORKSPACE.name}",
            mail.outbox[0].subject,
        )
        self.assertTrue(
            f"{settings.NEW_FRONTEND_DOMAIN}/user/account" in mail.outbox[0].body
        )

    def test_invite_workspace_member_workspace_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
                inviteWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        user {
                          email
                        }
                    }
                }
            }

            """,
            {
                "input": {
                    "workspaceSlug": str(uuid.uuid4()),
                    "userEmail": "root@openhexa.com",
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["WORKSPACE_NOT_FOUND"],
                "workspaceMembership": None,
            },
            r["data"]["inviteWorkspaceMember"],
        )

    def test_invite_workspace_member_workspace_already_exist(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
                inviteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "workspaceSlug": self.WORKSPACE.slug,
                    "userEmail": "rebecca@bluesquarehub.com",
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["ALREADY_EXISTS"],
            },
            r["data"]["inviteWorkspaceMember"],
        )

    def test_get_workspace_members(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            query workspaceBySlug($slug: String!) {
                workspace(slug: $slug) {
                    members {
                        items {
                            user {
                                id
                            }
                        }
                    }
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )

        self.assertEqual(
            {
                "items": [
                    {"user": {"id": str(self.USER_WORKSPACE_ADMIN.id)}},
                    {"user": {"id": str(self.USER_REBECCA.id)}},
                    {"user": {"id": str(self.USER_JULIA.id)}},
                ],
            },
            r["data"]["workspace"]["members"],
        )

    def test_delete_workspace_member_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspaceMember($input: DeleteWorkspaceMemberInput!) {
                deleteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(uuid.uuid4()),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["MEMBERSHIP_NOT_FOUND"],
            },
            r["data"]["deleteWorkspaceMember"],
        )

    def test_delete_workspace_member_permission_denied(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation deleteWorkspaceMember($input: DeleteWorkspaceMemberInput!) {
                deleteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["deleteWorkspaceMember"],
        )

    def test_delete_workspace_member(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspaceMember($input: DeleteWorkspaceMemberInput!) {
                deleteWorkspaceMember(input: $input) {
                    success
                    errors
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["deleteWorkspaceMember"],
        )

    def test_update_workspace_member_role_membership_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
                updateWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        role
                    }
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(uuid.uuid4()),
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["MEMBERSHIP_NOT_FOUND"],
                "workspaceMembership": None,
            },
            r["data"]["updateWorkspaceMember"],
        )

    def test_update_workspace_member_role_permission_denied(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation updateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
                updateWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        role
                    }
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP.id),
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "workspaceMembership": None,
            },
            r["data"]["updateWorkspaceMember"],
        )

    def test_update_workspace_member_role(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation updateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
                updateWorkspaceMember(input: $input) {
                    success
                    errors
                    workspaceMembership {
                        id
                        role
                    }
                }
            }

            """,
            {
                "input": {
                    "membershipId": str(self.WORKSPACE_MEMBERSHIP.id),
                    "role": WorkspaceMembershipRole.EDITOR,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "workspaceMembership": {
                    "id": str(self.WORKSPACE_MEMBERSHIP.id),
                    "role": WorkspaceMembershipRole.EDITOR,
                },
            },
            r["data"]["updateWorkspaceMember"],
        )

    def test_generate_workspace_token_non_authorized(self):
        # Test with a non authorized user
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
        mutation generateWorkspaceToken($input: GenerateWorkspaceTokenInput!) {
            generateWorkspaceToken(input: $input) {
                success
                errors
                token
            }
        }
        """,
            {
                "input": {
                    "slug": self.WORKSPACE_2.slug,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["WORKSPACE_NOT_FOUND"], "token": None},
            r["data"]["generateWorkspaceToken"],
        )

        self.client.force_login(self.USER_JULIA)
        r = self.run_query(
            """
        mutation generateWorkspaceToken($input: GenerateWorkspaceTokenInput!) {
            generateWorkspaceToken(input: $input) {
                success
                errors
                token
            }
        }
        """,
            {
                "input": {
                    "slug": self.WORKSPACE_2.slug,
                }
            },
        )

        token = WorkspaceMembership.objects.get(
            user=self.USER_JULIA, workspace=self.WORKSPACE_2
        ).access_token
        access_token = Signer().sign_object(str(token))
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "token": access_token,
            },
            r["data"]["generateWorkspaceToken"],
        )

    def test_invite_workspace_member_external_user(self):
        import random
        import string

        with patch("hexa.workspaces.models.TimestampSigner") as mocked_signer:
            random_string = "".join(random.choices(string.ascii_lowercase, k=10))

            signer = mocked_signer.return_value
            signer.sign.return_value = random_string

            encoded = base64.b64encode(random_string.encode("utf-8")).decode()
            user_email = "johndoe@foo.com"

            self.client.force_login(self.USER_WORKSPACE_ADMIN)
            r = self.run_query(
                """
                mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
                    inviteWorkspaceMember(input: $input) {
                        success
                        errors
                    }
                }
                """,
                {
                    "input": {
                        "workspaceSlug": self.WORKSPACE.slug,
                        "userEmail": user_email,
                        "role": WorkspaceMembershipRole.VIEWER,
                    }
                },
            )

            invitation = WorkspaceInvitation.objects.get(
                workspace=self.WORKSPACE, email=user_email
            )
            self.assertEqual(invitation.status, WorkspaceInvitationStatus.PENDING)
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                },
                r["data"]["inviteWorkspaceMember"],
            )
            self.assertEqual(
                f"You've been invited to join the workspace {self.WORKSPACE.name} on OpenHEXA",
                mail.outbox[0].subject,
            )
            self.assertListEqual([user_email], mail.outbox[0].recipients())
            self.assertIn(
                f"{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': user_email, 'token': encoded})}",
                mail.outbox[0].body,
            )

    def test_decline_workspace_invitation(self):
        self.client.force_login(self.USER_PENDING)
        r = self.run_query(
            """
            mutation declineWorkspaceInvitation($input: DeclineWorkspaceInvitationInput!) {
                declineWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_PENDING.id)}},
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["declineWorkspaceInvitation"],
        )

    def test_decline_workspace_invitation_already_accepted(self):
        self.client.force_login(self.USER_PENDING)
        self.INVITATION_PENDING.status = WorkspaceInvitationStatus.ACCEPTED
        self.INVITATION_PENDING.save()
        r = self.run_query(
            """
            mutation declineWorkspaceInvitation($input: DeclineWorkspaceInvitationInput!) {
                declineWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_PENDING.id)}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["declineWorkspaceInvitation"],
        )

    def test_decline_workspace_invitation_other_user(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation declineWorkspaceInvitation($input: DeclineWorkspaceInvitationInput!) {
                declineWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_PENDING.id)}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["declineWorkspaceInvitation"],
        )

    def test_decline_workspace_invitation_not_found(self):
        self.client.force_login(self.USER_PENDING)
        r = self.run_query(
            """
            mutation declineWorkspaceInvitation($input: DeclineWorkspaceInvitationInput!) {
                declineWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(uuid.uuid4())}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["INVITATION_NOT_FOUND"],
            },
            r["data"]["declineWorkspaceInvitation"],
        )

    def test_join_workspace_anonymous(self):
        r = self.run_query(
            """
            mutation joinWorkspace($input: JoinWorkspaceInput!) {
                joinWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "invitationId": str(self.INVITATION_FOO.id),
                }
            },
        )
        self.assertEqual(
            r["errors"][0]["extensions"],
            {"code": "UNAUTHENTICATED"},
        )

    def test_join_workspace_invitation_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation joinWorkspace($input: JoinWorkspaceInput!) {
                joinWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "invitationId": str(uuid.uuid4()),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["INVITATION_NOT_FOUND"],
            },
            r["data"]["joinWorkspace"],
        )

    def test_join_workspace_invitation_already_accepted(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation joinWorkspace($input: JoinWorkspaceInput!) {
                joinWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "invitationId": str(self.INVITATION_BAR.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["ALREADY_ACCEPTED"],
            },
            r["data"]["joinWorkspace"],
        )

    def test_join_workspace_invitation_already_member(self):
        self.client.force_login(self.USER_REBECCA)
        self.INVITATION_BAR.status = WorkspaceInvitationStatus.PENDING
        self.INVITATION_BAR.save()
        r = self.run_query(
            """
            mutation joinWorkspace($input: JoinWorkspaceInput!) {
                joinWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_BAR.id)}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["ALREADY_EXISTS"],
            },
            r["data"]["joinWorkspace"],
        )

    def test_join_workspace_different_authenticated_user(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation joinWorkspace($input: JoinWorkspaceInput!) {
                joinWorkspace(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_FOO.id)}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["joinWorkspace"],
        )

    def test_join_workspace_invitation_success(self):
        u = User.objects.create_user(self.USER_EXTERNAL, "password")
        self.client.force_login(u)

        r = self.run_query(
            """
        mutation joinWorkspace($input: JoinWorkspaceInput!) {
            joinWorkspace(input: $input) {
                success
                errors
            }
        }
        """,
            {"input": {"invitationId": str(self.INVITATION_FOO.id)}},
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["joinWorkspace"],
        )

    def test_empty_workspace_invitations(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            query{
                pendingWorkspaceInvitations {
                    totalItems
                    items {
                        email
                        role
                        status
                        invitedBy {
                            id
                        }
                    }
                }
            }
            """,
        )
        self.assertEqual(
            {
                "totalItems": 0,
                "items": [],
            },
            r["data"]["pendingWorkspaceInvitations"],
        )

    def test_pending_workspace_invitations(self):
        self.client.force_login(self.USER_PENDING)
        r = self.run_query(
            """
            query{
                pendingWorkspaceInvitations {
                    totalItems
                    items {
                        email
                        role
                        status
                        invitedBy {
                            id
                        }
                    }
                }
            }
            """,
        )
        self.assertEqual(
            {
                "totalItems": 1,
                "items": [
                    {
                        "email": self.INVITATION_PENDING.email,
                        "role": self.INVITATION_PENDING.role,
                        "status": WorkspaceInvitationStatus.PENDING,
                        "invitedBy": {"id": str(self.USER_WORKSPACE_ADMIN.id)},
                    }
                ],
            },
            r["data"]["pendingWorkspaceInvitations"],
        )

    def test_get_workspace_invitations(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            query workspaceBySlug($slug: String!) {
                workspace(slug: $slug) {
                    invitations {
                        totalItems
                        items {
                            email
                            role
                            status
                            invitedBy {
                                id
                            }
                        }
                    }
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )
        self.assertEqual(
            {
                "totalItems": 2,
                "items": [
                    {
                        "email": self.INVITATION_PENDING.email,
                        "role": self.INVITATION_PENDING.role,
                        "status": WorkspaceInvitationStatus.PENDING,
                        "invitedBy": {"id": str(self.USER_WORKSPACE_ADMIN.id)},
                    },
                    {
                        "email": self.INVITATION_FOO.email,
                        "role": self.INVITATION_FOO.role,
                        "status": WorkspaceInvitationStatus.PENDING,
                        "invitedBy": {"id": str(self.USER_WORKSPACE_ADMIN.id)},
                    },
                ],
            },
            r["data"]["workspace"]["invitations"],
        )
        r = self.run_query(
            """
            query workspaceBySlug($slug: String!) {
                workspace(slug: $slug) {
                    invitations(includeAccepted: true) {
                        totalItems
                        items {
                            email
                            role
                            status
                            invitedBy {
                                id
                            }
                        }
                    }
                }
            }
            """,
            {"slug": self.WORKSPACE.slug},
        )
        self.assertEqual(
            {
                "totalItems": 3,
                "items": [
                    {
                        "email": self.INVITATION_PENDING.email,
                        "role": self.INVITATION_PENDING.role,
                        "status": WorkspaceInvitationStatus.PENDING,
                        "invitedBy": {"id": str(self.USER_WORKSPACE_ADMIN.id)},
                    },
                    {
                        "email": self.INVITATION_BAR.email,
                        "role": self.INVITATION_BAR.role,
                        "status": WorkspaceInvitationStatus.ACCEPTED,
                        "invitedBy": {"id": str(self.USER_WORKSPACE_ADMIN.id)},
                    },
                    {
                        "email": self.INVITATION_FOO.email,
                        "role": self.INVITATION_FOO.role,
                        "status": WorkspaceInvitationStatus.PENDING,
                        "invitedBy": {"id": str(self.USER_WORKSPACE_ADMIN.id)},
                    },
                ],
            },
            r["data"]["workspace"]["invitations"],
        )

    def test_delete_workspace_invitation_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspaceInvitation($input: DeleteWorkspaceInvitationInput!) {
                deleteWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(uuid.uuid4())}},
        )
        self.assertEqual(
            {"success": False, "errors": ["INVITATION_NOT_FOUND"]},
            r["data"]["deleteWorkspaceInvitation"],
        )

    def test_delete_workspace_invitation_permission_denied(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation deleteWorkspaceInvitation($input: DeleteWorkspaceInvitationInput!) {
                deleteWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_FOO.id)}},
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteWorkspaceInvitation"],
        )

    def test_delete_workspace_invitation_already_accepted(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspaceInvitation($input: DeleteWorkspaceInvitationInput!) {
                deleteWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_BAR.id)}},
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteWorkspaceInvitation"],
        )

    def test_delete_workspace_invitation(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation deleteWorkspaceInvitation($input: DeleteWorkspaceInvitationInput!) {
                deleteWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_FOO.id)}},
        )
        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteWorkspaceInvitation"],
        )

    def test_resend_workspace_member_invitation_not_found(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation resendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
                resendWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(uuid.uuid4())}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["INVITATION_NOT_FOUND"],
            },
            r["data"]["resendWorkspaceInvitation"],
        )

    def test_resend_workspace_member_invitation_permission_denied(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
            mutation resendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
                resendWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_FOO.id)}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["resendWorkspaceInvitation"],
        )

    def test_resend_workspace_member_invitation_already_accepted(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation resendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
                resendWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_BAR.id)}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["INVITATION_NOT_FOUND"],
            },
            r["data"]["resendWorkspaceInvitation"],
        )

    def test_resend_invitation_declined(self):
        self.INVITATION_BAR.status = WorkspaceInvitationStatus.DECLINED
        self.INVITATION_BAR.save()

        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
            mutation resendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
                resendWorkspaceInvitation(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"invitationId": str(self.INVITATION_BAR.id)}},
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["resendWorkspaceInvitation"],
        )

        self.assertEqual(
            f"You've been added to the workspace {self.WORKSPACE.name}",
            mail.outbox[0].subject,
        )
        self.assertListEqual([self.INVITATION_BAR.email], mail.outbox[0].recipients())
        self.INVITATION_BAR.refresh_from_db()
        self.assertEqual(self.INVITATION_BAR.status, WorkspaceInvitationStatus.PENDING)

    def test_resend_workspace_member_invitation(self):
        import random
        import string

        with patch("hexa.workspaces.models.TimestampSigner") as mocked_signer:
            random_string = "".join(random.choices(string.ascii_lowercase, k=10))

            signer = mocked_signer.return_value
            signer.sign.return_value = random_string

            encoded = base64.b64encode(random_string.encode("utf-8")).decode()
            user_email = self.INVITATION_FOO.email

            self.client.force_login(self.USER_WORKSPACE_ADMIN)
            r = self.run_query(
                """
                mutation resendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
                    resendWorkspaceInvitation(input: $input) {
                        success
                        errors
                    }
                }
                """,
                {"input": {"invitationId": str(self.INVITATION_FOO.id)}},
            )
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                },
                r["data"]["resendWorkspaceInvitation"],
            )
            self.assertEqual(
                f"You've been invited to join the workspace {self.WORKSPACE.name} on OpenHEXA",
                mail.outbox[0].subject,
            )
            self.assertListEqual([user_email], mail.outbox[0].recipients())
            self.assertIn(
                f"{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': user_email, 'token': encoded})}",
                mail.outbox[0].body,
            )

    def test_resend_workspace_member_invitation_existing_user(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        r = self.run_query(
            """
                mutation resendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
                    resendWorkspaceInvitation(input: $input) {
                        success
                        errors
                    }
                }
                """,
            {"input": {"invitationId": str(self.INVITATION_PENDING.id)}},
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["resendWorkspaceInvitation"],
        )
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(
            f"You've been added to the workspace {self.INVITATION_FOO.workspace.name}",
            mail.outbox[0].subject,
        )
        self.assertTrue(
            f"{settings.NEW_FRONTEND_DOMAIN}/user/account" in mail.outbox[0].body
        )

    def test_delete_workspace_database_table_permission_denied(self):
        self.client.force_login(self.USER_REBECCA)
        r = self.run_query(
            """
                mutation deleteWorkspaceDatabaseTable($input: DeleteWorkspaceDatabaseTableInput!) {
                    deleteWorkspaceDatabaseTable(input: $input) {
                        success
                        errors
                    }
                }
                """,
            {"input": {"workspaceSlug": self.WORKSPACE.slug, "table": "foo"}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["deleteWorkspaceDatabaseTable"],
        )

    def test_delete_workspace_database_table_not_found(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        with patch(
            "hexa.workspaces.schema.mutations.delete_table"
        ) as mocked_get_table_definition:
            mocked_get_table_definition.side_effect = TableNotFound(
                "Table foo doesn't exist"
            )

            r = self.run_query(
                """
                    mutation deleteWorkspaceDatabaseTable($input: DeleteWorkspaceDatabaseTableInput!) {
                        deleteWorkspaceDatabaseTable(input: $input) {
                            success
                            errors
                        }
                    }
                    """,
                {"input": {"workspaceSlug": self.WORKSPACE.slug, "table": "foo"}},
            )
            self.assertEqual(
                {
                    "success": False,
                    "errors": ["TABLE_NOT_FOUND"],
                },
                r["data"]["deleteWorkspaceDatabaseTable"],
            )

    def test_delete_workspace_database_table(self):
        self.client.force_login(self.USER_WORKSPACE_ADMIN)
        with patch("hexa.workspaces.schema.mutations.delete_table"):
            r = self.run_query(
                """
                    mutation deleteWorkspaceDatabaseTable($input: DeleteWorkspaceDatabaseTableInput!) {
                        deleteWorkspaceDatabaseTable(input: $input) {
                            success
                            errors
                        }
                    }
                    """,
                {"input": {"workspaceSlug": self.WORKSPACE.slug, "table": "foo"}},
            )
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                },
                r["data"]["deleteWorkspaceDatabaseTable"],
            )
