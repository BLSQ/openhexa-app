import re
from unittest.mock import patch

from django.core import mail
from django.test import override_settings
from django.utils.http import urlsafe_base64_encode
from django_otp import user_has_device
from django_otp.models import Device

from hexa.core.test import GraphQLTestCase
from hexa.core.test.utils import graphql_datetime_format
from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Membership,
    MembershipRole,
    Organization,
    OrganizationInvitation,
    OrganizationInvitationStatus,
    OrganizationMembership,
    OrganizationMembershipRole,
    SignupRequest,
    SignupRequestStatus,
    Team,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceInvitation,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

from ..utils import default_device, devices_for_user


class SchemaTest(GraphQLTestCase):
    USER_JIM = None
    USER_JANE = None
    USER_TAYLOR = None
    TEAM_CORE = None
    TEAM_EXTERNAL = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_JIM = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimspassword",
        )
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janespassword",
        )
        cls.USER_TAYLOR = User.objects.create_user(
            "taylor@bluesquarehub.com",
            "taylortaylor2000",
        )
        cls.USER_STAFF_NICO = User.objects.create_user(
            "nico@bluesquarehub.com", "nicodu93", is_staff=True
        )
        cls.SUPER_USER_ALF = User.objects.create_user(
            "alf@bluesquarehub.com", "alfdu96", is_superuser=True, is_staff=True
        )
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com",
            "adminadmin2022",
            is_staff=True,
            first_name="Ad",
            last_name="Min",
        )
        cls.TEAM_CORE = Team.objects.create(name="Core team")
        cls.MEMBERSHIP_JANE_CORE = Membership.objects.create(
            user=cls.USER_JANE, team=cls.TEAM_CORE, role=MembershipRole.ADMIN
        )
        cls.MEMBERSHIP_JIM_CORE = Membership.objects.create(
            user=cls.USER_JIM, team=cls.TEAM_CORE, role=MembershipRole.REGULAR
        )
        cls.TEAM_EXTERNAL = Team.objects.create(name="External team")
        Membership.objects.create(
            user=cls.USER_TAYLOR, team=cls.TEAM_EXTERNAL, role=MembershipRole.ADMIN
        )

        cls.FEATURE = Feature.objects.create(code="nice_feature")
        cls.TAYLOR_FEATURE_FLAG = FeatureFlag.objects.create(
            feature=cls.FEATURE, user=cls.USER_TAYLOR
        )

        cls.USER_JANE.emaildevice_set.create(name="default", user=cls.USER_JANE)

    def test_me_anonymous(self):
        r = self.run_query(
            """
              query {
                me {
                  user {
                    id
                  }
                  features {
                    code
                  }
                  permissions {
                    createTeam
                    adminPanel
                    superUser
                  }
                }
              }
            """,
        )

        self.assertEqual(
            {
                "me": {
                    "features": [],
                    "user": None,
                    "permissions": {
                        "createTeam": False,
                        "adminPanel": False,
                        "superUser": False,
                    },
                }
            },
            r["data"],
        )

    def test_me(self):
        self.client.force_login(self.USER_JIM)
        r = self.run_query(
            """
              query {
                me {
                  user {
                    id
                    firstName
                    lastName
                    displayName
                    email
                    dateJoined
                    lastLogin
                  }
                  features {
                    code
                  }
                  permissions {
                    createTeam
                    adminPanel
                  }
                }
              }
            """,
        )

        self.assertEqual(
            {
                "user": {
                    "id": str(self.USER_JIM.id),
                    "firstName": self.USER_JIM.first_name,
                    "lastName": self.USER_JIM.last_name,
                    "displayName": self.USER_JIM.display_name,
                    "email": self.USER_JIM.email,
                    "dateJoined": graphql_datetime_format(self.USER_JIM.date_joined),
                    "lastLogin": (
                        graphql_datetime_format(self.USER_JIM.last_login)
                        if self.USER_JIM.last_login
                        else None
                    ),
                },
                "features": [],
                "permissions": {"createTeam": True, "adminPanel": False},
            },
            r["data"]["me"],
        )

    def test_me_features(self):
        self.client.force_login(self.USER_TAYLOR)
        r = self.run_query(
            """
              query {
                me {
                  features {
                    code
                  }
                  user {
                    id
                  }
                }
              }
            """,
        )

        self.assertEqual(
            {
                "features": [
                    {
                        "code": self.TAYLOR_FEATURE_FLAG.feature.code,
                    }
                ],
                "user": {
                    "id": str(self.USER_TAYLOR.id),
                },
            },
            r["data"]["me"],
        )

    def test_teams_1(self):
        self.client.force_login(self.USER_JIM)

        r = self.run_query(
            """
              query teams {
                teams {
                  pageNumber
                  totalPages
                  totalItems
                  items {
                    id
                    name
                    createdAt
                    updatedAt
                    memberships {
                      pageNumber
                      totalPages
                      totalItems
                      items {
                        user {
                          id
                        }
                        team {
                          id
                        }
                        role
                        createdAt
                        updatedAt
                      }
                    }
                  }
                }
              }
            """,
        )

        self.assertEqual(
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {
                        "id": str(self.TEAM_CORE.id),
                        "name": self.TEAM_CORE.name,
                        "createdAt": graphql_datetime_format(self.TEAM_CORE.created_at),
                        "updatedAt": graphql_datetime_format(self.TEAM_CORE.updated_at),
                        "memberships": {
                            "pageNumber": 1,
                            "totalPages": 1,
                            "totalItems": 2,
                            "items": [
                                {
                                    "user": {"id": str(self.USER_JANE.id)},
                                    "team": {"id": str(self.TEAM_CORE.id)},
                                    "role": MembershipRole.ADMIN,
                                    "createdAt": graphql_datetime_format(
                                        self.MEMBERSHIP_JANE_CORE.created_at
                                    ),
                                    "updatedAt": graphql_datetime_format(
                                        self.MEMBERSHIP_JANE_CORE.updated_at
                                    ),
                                },
                                {
                                    "user": {"id": str(self.USER_JIM.id)},
                                    "team": {"id": str(self.TEAM_CORE.id)},
                                    "role": MembershipRole.REGULAR,
                                    "createdAt": graphql_datetime_format(
                                        self.MEMBERSHIP_JIM_CORE.created_at
                                    ),
                                    "updatedAt": graphql_datetime_format(
                                        self.MEMBERSHIP_JIM_CORE.updated_at
                                    ),
                                },
                            ],
                        },
                    },
                ],
            },
            r["data"]["teams"],
        )

    def test_teams_2(self):
        self.client.force_login(self.USER_TAYLOR)

        r = self.run_query(
            """
              query teams {
                teams {
                  pageNumber
                  totalPages
                  totalItems
                  items {
                    id
                    name
                    memberships {
                      pageNumber
                      totalPages
                      totalItems
                      items {
                        user {
                          id
                        }
                        team {
                          id
                        }
                        role
                      }
                    }
                  }
                }
              }
            """,
        )

        self.assertEqual(
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {
                        "id": str(self.TEAM_EXTERNAL.id),
                        "name": self.TEAM_EXTERNAL.name,
                        "memberships": {
                            "pageNumber": 1,
                            "totalPages": 1,
                            "totalItems": 1,
                            "items": [
                                {
                                    "user": {"id": str(self.USER_TAYLOR.id)},
                                    "team": {"id": str(self.TEAM_EXTERNAL.id)},
                                    "role": MembershipRole.ADMIN,
                                },
                            ],
                        },
                    },
                ],
            },
            r["data"]["teams"],
        )

    def test_team_not_member(self):
        self.client.force_login(self.USER_TAYLOR)

        r = self.run_query(
            """
              query team($id: UUID!) {
                team(id: $id) {
                  id
                  name
                  memberships {
                    pageNumber
                    totalPages
                    totalItems
                  }
                }
              }
            """,
            {"id": str(self.TEAM_CORE.id)},
        )

        self.assertIsNone(
            r["data"]["team"],
        )

    def test_team_member(self):
        self.client.force_login(self.USER_TAYLOR)

        r = self.run_query(
            """
              query team($id: UUID!) {
                team(id: $id) {
                  id
                  name
                  memberships {
                    pageNumber
                    totalPages
                    totalItems
                  }
                }
              }
            """,
            {"id": str(self.TEAM_EXTERNAL.id)},
        )

        self.assertEqual(
            {
                "id": str(self.TEAM_EXTERNAL.id),
                "name": self.TEAM_EXTERNAL.name,
                "memberships": {"pageNumber": 1, "totalPages": 1, "totalItems": 1},
            },
            r["data"]["team"],
        )

    def test_login_without_two_factor(self):
        r = self.run_query(
            """
              mutation login($input: LoginInput!) {
                login(input: $input) {
                  success
                }
              }
            """,
            {"input": {"email": "jim@bluesquarehub.com", "password": "jimspassword"}},
        )

        self.assertEqual(
            {"success": True},
            r["data"]["login"],
        )

    def test_login_with_whitespace(self):
        r = self.run_query(
            """
              mutation login($input: LoginInput!) {
                login(input: $input) {
                  success
                }
              }
            """,
            {"input": {"email": " jim@bluesquarehub.com", "password": "jimspassword"}},
        )

        self.assertEqual(
            {"success": True},
            r["data"]["login"],
        )

    def test_login_invalid_credentials(self):
        r = self.run_query(
            """
              mutation login($input: LoginInput!) {
                login(input: $input) {
                  success
                  errors
                }
              }
            """,
            {"input": {"email": self.USER_JANE.email, "password": "invalid"}},
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID_CREDENTIALS"]}, r["data"]["login"]
        )

    def test_login_invalid_otp(self):
        r = self.run_query(
            """
              mutation login($input: LoginInput!) {
                login(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "email": self.USER_JANE.email,
                    "password": "janespassword",
                    "token": "123",
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID_OTP"]}, r["data"]["login"]
        )

    def test_login_unconfirmed_device(self):
        """
        It should act as a normal login without two factor
        """

    def test_login_valid_otp(self):
        device = default_device(self.USER_JANE)
        device.generate_challenge()
        r = self.run_query(
            """
              mutation login($input: LoginInput!) {
                login(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "email": self.USER_JANE.email,
                    "password": "janespassword",
                    "token": device.token,
                }
            },
        )
        self.assertEqual({"success": True, "errors": None}, r["data"]["login"])

    def test_logout(self):
        self.client.force_login(self.USER_JIM)
        r = self.run_query(
            """
              query {
                me {
                  user {
                    id
                  }
                }
              }
            """,
        )
        self.assertEqual(
            {"user": {"id": str(self.USER_JIM.id)}},
            r["data"]["me"],
        )

        r = self.run_query(
            """
              mutation {
                logout {
                  success
                }
              }
            """,
        )

        self.assertEqual(
            {
                "success": True,
            },
            r["data"]["logout"],
        )

        r = self.run_query(
            """
              query {
                me {
                  user {
                    id
                  }
                }
              }
            """,
        )
        self.assertEqual(
            {"user": None},
            r["data"]["me"],
        )

    @override_settings(NEW_FRONTEND_DOMAIN="https://newfrontend.example.com")
    def test_reset_password(self):
        r = self.run_query(
            """
                  mutation resetPassword($input: ResetPasswordInput!) {
                    resetPassword(input: $input) {
                      success
                    }
                  }
                """,
            {"input": {"email": self.USER_JIM.email}},
        )

        self.assertEqual(
            {"success": True},
            r["data"]["resetPassword"],
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            "Please go to the following page and choose a new password:",
            mail.outbox[0].body,
        )
        self.assertIn(
            "https://newfrontend.example.com/auth/reset/", mail.outbox[0].body
        )
        self.assertEqual(
            mail.outbox[0].subject,
            "Password reset on newfrontend.example.com",
        )

    def test_reset_password_wrong_email(self):
        r = self.run_query(
            """
              mutation resetPassword($input: ResetPasswordInput!) {
                resetPassword(input: $input) {
                  success
                }
              }
            """,
            {"input": {"email": "unkonwn@bluesquarehub.com"}},
        )

        self.assertEqual(
            {"success": True},
            r["data"]["resetPassword"],
        )

        self.assertEqual(len(mail.outbox), 0)

    def _test_reset_start(self):  # TODO: use setupData
        # Start by creating the email
        self.run_query(
            """
              mutation resetPassword($input: ResetPasswordInput!) {
                resetPassword(input: $input) {
                  success
                }
              }
            """,
            {"input": {"email": self.USER_JIM.email}},
        )
        self.assertEqual(len(mail.outbox), 1)
        return self._extract_tokens_from_email(mail.outbox[0])

    def _extract_tokens_from_email(self, email):
        urlmatch = re.search(r"https?://[^/]*.*reset/([\w_-]*)/([\w_-]*)", email.body)
        self.assertIsNotNone(urlmatch, "No URL found in sent email")
        return urlmatch[1], urlmatch[2]

    def test_set_password_success(self):
        uidb64, token = self._test_reset_start()
        password1 = "alfonse_brown"
        password2 = "alfonse_brown"
        existing_pwd = self.USER_JIM.password

        r = self.run_query(
            """
              mutation setPassword($input: SetPasswordInput!) {
                setPassword(input: $input) {
                  error
                  success
                }
              }
            """,
            {
                "input": {
                    "token": token,
                    "uidb64": uidb64,
                    "password1": password1,
                    "password2": password2,
                }
            },
        )

        self.assertEqual(
            {"success": True, "error": None},
            r["data"]["setPassword"],
        )
        self.USER_JIM.refresh_from_db()
        self.assertNotEqual(existing_pwd, self.USER_JIM.password)

    def test_set_password_invalid_token(self):
        uidb64, token = self._test_reset_start()
        password1 = "very_long_password_provid3d"
        password2 = "very_long_password_provid3d"

        r = self.run_query(
            """
              mutation setPassword($input: SetPasswordInput!) {
                setPassword(input: $input) {
                  error
                  success
                }
              }
            """,
            {
                "input": {
                    "token": token[:-3],  # Shorten the token to make it invalid
                    "uidb64": uidb64,
                    "password1": password1,
                    "password2": password2,
                }
            },
        )

        self.assertEqual(
            {"success": False, "error": "INVALID_TOKEN"},
            r["data"]["setPassword"],
        )

    def test_set_password_invalid_password(self):
        uidb64, token = self._test_reset_start()
        password1 = "short"
        password2 = "short"

        r = self.run_query(
            """
              mutation setPassword($input: SetPasswordInput!) {
                setPassword(input: $input) {
                  error
                  success
                }
              }
            """,
            {
                "input": {
                    "token": token,
                    "uidb64": uidb64,
                    "password1": password1,
                    "password2": password2,
                }
            },
        )

        self.assertEqual(
            {"success": False, "error": "INVALID_PASSWORD"},
            r["data"]["setPassword"],
        )

    def test_set_password_invalid_uid(self):
        uidb64, token = self._test_reset_start()
        password1 = "very_long_password_provid3d"
        password2 = "very_long_password_provid3d"

        r = self.run_query(
            """
              mutation setPassword($input: SetPasswordInput!) {
                setPassword(input: $input) {
                  error
                  success
                }
              }
            """,
            {
                "input": {
                    "token": token,
                    "uidb64": uidb64[:-3],
                    "password1": password1,
                    "password2": password2,
                }
            },
        )

        self.assertEqual(
            {"success": False, "error": "INVALID_TOKEN"},
            r["data"]["setPassword"],
        )

    def test_set_password_unknown_user(self):
        _, token = self._test_reset_start()
        password1 = "very_long_password_provid3d"
        password2 = "very_long_password_provid3d"

        r = self.run_query(
            """
              mutation setPassword($input: SetPasswordInput!) {
                setPassword(input: $input) {
                  error
                  success
                }
              }
            """,
            {
                "input": {
                    "token": token,
                    "uidb64": urlsafe_base64_encode(b"2"),
                    "password1": password1,
                    "password2": password2,
                }
            },
        )

        self.assertEqual(
            {"success": False, "error": "INVALID_TOKEN"},
            r["data"]["setPassword"],
        )

    def test_set_password_invalid(self):
        uidb64, token = self._test_reset_start()
        password1 = ""
        password2 = ""

        r = self.run_query(
            """
              mutation setPassword($input: SetPasswordInput!) {
                setPassword(input: $input) {
                  error
                  success
                }
              }
            """,
            {
                "input": {
                    "token": token,
                    "uidb64": uidb64,
                    "password1": password1,
                    "password2": password2,
                }
            },
        )

        self.assertEqual(
            {"success": False, "error": "PASSWORD_MISMATCH"},
            r["data"]["setPassword"],
        )

    def test_create_membership(self):
        self.client.force_login(self.USER_JANE)

        with patch(
            "hexa.user_management.permissions.create_membership"
        ) as create_membership:
            r = self.run_query(
                """
                  mutation createMembership($input: CreateMembershipInput!) {
                    createMembership(input: $input) {
                      success
                      membership {
                        user { id }
                        team { id }
                        role
                      }
                    }
                  }
                """,
                {
                    "input": {
                        "userEmail": self.USER_TAYLOR.email,
                        "teamId": str(self.TEAM_CORE.id),
                        "role": MembershipRole.REGULAR,
                    },
                },
            )

        create_membership.assert_called_once_with(self.USER_JANE, self.TEAM_CORE)
        self.assertEqual(
            {
                "success": True,
                "membership": {
                    "user": {"id": str(self.USER_TAYLOR.id)},
                    "team": {"id": str(self.TEAM_CORE.id)},
                    "role": MembershipRole.REGULAR,
                },
            },
            r["data"]["createMembership"],
        )

    def test_create_membership_already_exists(self):
        self.client.force_login(self.USER_JANE)

        r = self.run_query(
            """
              mutation createMembership($input: CreateMembershipInput!) {
                createMembership(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "userEmail": self.USER_JANE.email,
                    "teamId": str(self.TEAM_CORE.id),
                    "role": MembershipRole.REGULAR,
                },
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["ALREADY_EXISTS"],
            },
            r["data"]["createMembership"],
        )

    def test_update_membership(self):
        self.client.force_login(self.USER_JANE)

        with patch(
            "hexa.user_management.permissions.update_membership"
        ) as update_membership:
            r = self.run_query(
                """
                  mutation updateMembership($input: UpdateMembershipInput!) {
                    updateMembership(input: $input) {
                      success
                      membership {
                        role
                      }
                    }
                  }
                """,
                {
                    "input": {
                        "id": str(self.MEMBERSHIP_JIM_CORE.id),
                        "role": MembershipRole.ADMIN,
                    },
                },
            )

        update_membership.assert_called_once_with(
            self.USER_JANE, self.MEMBERSHIP_JIM_CORE
        )
        self.assertEqual(
            {
                "success": True,
                "membership": {
                    "role": MembershipRole.ADMIN,
                },
            },
            r["data"]["updateMembership"],
        )

    def test_update_membership_error(self):
        self.client.force_login(self.USER_JANE)

        r = self.run_query(
            """
              mutation updateMembership($input: UpdateMembershipInput!) {
                updateMembership(input: $input) {
                  success
                  errors
                }
              }
            """,
            {
                "input": {
                    "id": str(self.MEMBERSHIP_JANE_CORE.id),
                    "role": MembershipRole.REGULAR,
                },
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["INVALID_ROLE"]},
            r["data"]["updateMembership"],
        )

    def test_delete_membership(self):
        self.client.force_login(self.USER_JANE)

        with patch(
            "hexa.user_management.permissions.delete_membership"
        ) as delete_membership:
            r = self.run_query(
                """
                  mutation deleteMembership($input: DeleteMembershipInput!) {
                    deleteMembership(input: $input) {
                      success
                    }
                  }
                """,
                {
                    "input": {
                        "id": str(self.MEMBERSHIP_JIM_CORE.id),
                    },
                },
            )

        delete_membership.assert_called_once()  # Cannot use called_once_with() as membership has been deleted
        self.assertEqual(
            {
                "success": True,
            },
            r["data"]["deleteMembership"],
        )

    def test_delete_membership_error(self):
        self.client.force_login(self.USER_JANE)

        r = self.run_query(
            """
              mutation deleteMembership($input: DeleteMembershipInput!) {
                deleteMembership(input: $input) {
                  success
                }
              }
            """,
            {
                "input": {
                    "id": str(self.MEMBERSHIP_JANE_CORE.id),
                },
            },
        )
        self.assertEqual(
            {
                "success": False,
            },
            r["data"]["deleteMembership"],
        )

    def test_staff_authorized_action(self):
        self.client.force_login(self.USER_STAFF_NICO)
        r = self.run_query(
            """
            query {
              me {
                user {
                  id
                }
                permissions {
                    createTeam
                    adminPanel
                    createAccessmodProject
                }
              }
            }
          """,
        )

        self.assertEqual(
            {
                "user": {
                    "id": str(self.USER_STAFF_NICO.id),
                },
                "permissions": {
                    "createTeam": True,
                    "adminPanel": True,
                    "createAccessmodProject": True,
                },
            },
            r["data"]["me"],
        )

    def test_super_user_authorized_action(self):
        self.client.force_login(self.SUPER_USER_ALF)
        r = self.run_query(
            """
            query {
              me {
                user {
                  id
                }
                permissions {
                    createTeam
                    adminPanel
                    superUser
                    createAccessmodProject
                    manageAccessmodAccessRequests
                }
              }
            }
          """,
        )

        self.assertEqual(
            {
                "user": {
                    "id": str(self.SUPER_USER_ALF.id),
                },
                "permissions": {
                    "createTeam": True,
                    "adminPanel": True,
                    "superUser": True,
                    "createAccessmodProject": True,
                    "manageAccessmodAccessRequests": True,
                },
            },
            r["data"]["me"],
        )

    def test_search_users_success_all(self):
        workspace = Workspace.objects.create(name="Workspace", slug="workspace")
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=self.USER_JANE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        self.client.force_login(self.USER_JANE)
        r = self.run_query(
            """
            query ($query: String!, $workspaceSlug: String!) {
                users (query: $query, workspaceSlug: $workspaceSlug) {
                    email
                    firstName
                    lastName
                }
            }
            """,
            {"query": "", "workspaceSlug": workspace.slug},
        )

        users = r["data"]["users"]
        # There are 6 users created in `setUpTestData` method.
        # The search finds all except the logged in user (Jane).
        self.assertEqual(User.objects.count(), 6)
        self.assertEqual(len(users), 5)
        self.assertEqual(
            {"email": self.USER_ADMIN.email, "firstName": "Ad", "lastName": "Min"},
            users[0],
        )

    def test_search_users_success_with_query(self):
        workspace = Workspace.objects.create(name="Workspace", slug="workspace")
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=self.USER_JANE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        self.client.force_login(self.USER_JANE)
        r = self.run_query(
            """
            query ($query: String!, $workspaceSlug: String!) {
                users (query: $query, workspaceSlug: $workspaceSlug) {
                    email
                    firstName
                    lastName
                }
            }
            """,
            {"query": "taylor", "workspaceSlug": workspace.slug},
        )
        self.assertEqual(len(r["data"]["users"]), 1)
        self.assertEqual(
            {"email": self.USER_TAYLOR.email, "firstName": "", "lastName": ""},
            r["data"]["users"][0],
        )

    def test_search_users_invalid_workspace(self):
        self.client.force_login(self.USER_JANE)
        r = self.run_query(
            """
            query ($query: String!, $workspaceSlug: String!) {
                users (query: $query, workspaceSlug: $workspaceSlug) {
                    email
                    firstName
                    lastName
                }
            }
            """,
            {"query": "", "workspaceSlug": "unexisting"},
        )
        self.assertEqual([], r["data"]["users"])

    def test_search_users_not_admin(self):
        workspace = Workspace.objects.create(name="Workspace", slug="workspace")
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=self.USER_JANE,
            role=WorkspaceMembershipRole.VIEWER,
        )
        self.client.force_login(self.USER_JANE)
        r = self.run_query(
            """
            query ($query: String!, $workspaceSlug: String!) {
                users (query: $query, workspaceSlug: $workspaceSlug) {
                    email
                    firstName
                    lastName
                }
            }
            """,
            {"query": "", "workspaceSlug": workspace.slug},
        )
        self.assertEqual([], r["data"]["users"])

    def test_search_users_missing_parameters(self):
        self.client.force_login(self.USER_JANE)
        r = self.run_query(
            """
            query ($query: String!) {
                users (query: $query) {
                    email
                    firstName
                    lastName
                }
            }
            """,
            {"query": ""},
        )
        self.assertIn("errors", r)
        self.assertIn(
            "You must specify either a workspaceSlug or an organizationId",
            str(r["errors"]),
        )


class TwoFactorTest(GraphQLTestCase):
    @classmethod
    def setUp(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com", "regular", first_name="John"
        )
        cls.USER_WITH_DEVICE = User.objects.create_user(
            "device@bluesquare.com", "device"
        )
        cls.USER_WITH_DEVICE_2 = User.objects.create_user(
            "device2@bluesquare.com", "device"
        )
        cls.USER_WITHOUT_DEVICE = User.objects.create_user(
            "rebecca@bluesquare.com", "device"
        )
        cls.USER_WITH_DEVICE.emaildevice_set.create(
            name="default", user=cls.USER_WITH_DEVICE
        ).save()
        cls.USER_WITH_DEVICE_2.emaildevice_set.create(
            name="default", user=cls.USER_WITH_DEVICE_2
        ).save()

    def test_me_without_two_factor(self):
        self.client.force_login(self.USER_REGULAR)
        r = self.run_query(
            """
            query {
                me {
                    hasTwoFactorEnabled
                    user {
                        id
                        email
                    }
                }
            }
        """
        )

        self.assertEqual(
            {
                "hasTwoFactorEnabled": False,
                "user": {
                    "id": str(self.USER_REGULAR.id),
                    "email": self.USER_REGULAR.email,
                },
            },
            r["data"]["me"],
        )

    def test_enable_two_factor(self):
        self.client.force_login(self.USER_REGULAR)
        self.assertFalse(user_has_device(self.USER_REGULAR, confirmed=False))
        self.assertFalse(user_has_device(self.USER_REGULAR, confirmed=True))
        r = self.run_query(
            """
                mutation enableTwoFactor {
                    enableTwoFactor {
                        success
                    }
                }
            """,
        )

        self.assertEqual({"enableTwoFactor": {"success": True}}, r["data"])
        self.assertTrue(user_has_device(self.USER_REGULAR, confirmed=False))
        self.assertFalse(user_has_device(self.USER_REGULAR, confirmed=True))
        self.assertTrue(len(mail.outbox), 1)

    def test_enable_two_factor_already_enabled(self):
        self.client.force_login(self.USER_WITH_DEVICE)

        self.assertTrue(user_has_device(self.USER_WITH_DEVICE))
        r = self.run_query(
            """
                mutation enableTwoFactor {
                    enableTwoFactor {
                        success
                        errors
                    }
                }
            """,
        )

        self.assertEqual(
            {"success": False, "errors": ["ALREADY_ENABLED"]},
            r["data"]["enableTwoFactor"],
        )

    def test_enable_two_factor_unconfirmed_device_present(self):
        self.client.force_login(self.USER_WITH_DEVICE)
        device = default_device(self.USER_WITH_DEVICE)
        device.confirmed = False
        device.save()
        r = self.run_query(
            """
                mutation enableTwoFactor {
                    enableTwoFactor {
                        success
                        errors
                        verified
                    }
                }
            """,
        )
        self.assertEqual(
            {"success": True, "verified": False, "errors": []},
            r["data"]["enableTwoFactor"],
        )
        self.assertEqual(
            1, len(list(devices_for_user(self.USER_WITH_DEVICE, confirmed=None)))
        )

    def test_generate_challenge(self):
        self.client.force_login(self.USER_WITH_DEVICE)
        r = self.run_query(
            """
                mutation generateChallenge {
                    generateChallenge {
                        success
                        errors
                    }
                }
            """
        )

        self.assertEqual(
            {"success": True, "errors": None}, r["data"]["generateChallenge"]
        )
        self.assertTrue(len(mail.outbox), 1)

    def test_verify_unconfirmed_device(self):
        self.client.force_login(self.USER_WITHOUT_DEVICE)
        r = self.run_query(
            """
            mutation {
              enableTwoFactor{
                success
              }
            }
          """
        )
        self.assertEqual({"success": True}, r["data"]["enableTwoFactor"])
        device = default_device(self.USER_WITHOUT_DEVICE, confirmed=False)
        r = self.run_query(
            """
                mutation verifyDevice($input: VerifyDeviceInput!) {
                    verifyDevice(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"token": device.token}},
        )

        self.assertEqual({"success": True, "errors": []}, r["data"]["verifyDevice"])

    def test_verify_existing_device_bad_token(self):
        self.client.force_login(self.USER_WITH_DEVICE)
        device: Device = default_device(self.USER_WITH_DEVICE)
        device.confirmed = False
        device.save()
        r = self.run_query(
            """
                mutation verifyDevice($input: VerifyDeviceInput!) {
                    verifyDevice(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"token": "X"}},
        )

        self.assertEqual(
            {"success": False, "errors": ["INVALID_OTP"]},
            r["data"]["verifyDevice"],
        )

    def test_verify_with_another_user_device(self):
        self.client.force_login(self.USER_WITHOUT_DEVICE)
        device: Device = default_device(self.USER_WITH_DEVICE_2)
        device.generate_challenge()
        r = self.run_query(
            """
                mutation verifyDevice($input: VerifyDeviceInput!) {
                    verifyDevice(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"token": device.token}},
        )
        self.assertEqual(
            {"success": False, "errors": ["NO_DEVICE"]},
            r["data"]["verifyDevice"],
        )

    def test_disable_two_factor_unverified(self):
        self.client.force_login(self.USER_WITH_DEVICE)
        device: Device = default_device(self.USER_WITH_DEVICE)
        device.generate_challenge()
        r = self.run_query(
            """
                mutation disableTwoFactor($input: DisableTwoFactorInput!) {
                    disableTwoFactor(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"token": device.token}},
        )

        self.assertEqual(
            {"success": True, "errors": None}, r["data"]["disableTwoFactor"]
        )

    def test_disable_two_factor(self):
        self.client.force_login(self.USER_WITH_DEVICE)

        device: Device = default_device(self.USER_WITH_DEVICE)
        device.generate_challenge()
        r = self.run_query(
            """
                mutation disableTwoFactor($input: DisableTwoFactorInput!) {
                    disableTwoFactor(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"token": device.token}},
        )

        self.assertEqual(
            r["data"]["disableTwoFactor"], {"success": True, "errors": None}
        )

    def test_update_user(self):
        self.client.force_login(self.USER_REGULAR)

        self.assertEqual(self.USER_REGULAR.language, "en")
        self.assertEqual(self.USER_REGULAR.first_name, "John")
        r = self.run_query(
            """
                mutation updateUser($input: UpdateUserInput!) {
                    updateUser(input: $input) {
                        success
                        errors
                        user {
                            id
                            email
                            firstName
                            language
                        }
                    }
                }
            """,
            {"input": {"firstName": "New first name", "language": "fr"}},
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "user": {
                    "id": str(self.USER_REGULAR.id),
                    "email": self.USER_REGULAR.email,
                    "firstName": "New first name",
                    "language": "fr",
                },
            },
            r["data"]["updateUser"],
        )
        self.USER_REGULAR.refresh_from_db()
        self.assertEqual(self.USER_REGULAR.first_name, "New first name")
        self.assertEqual(self.USER_REGULAR.language, "fr")

    @override_settings(LANGUAGES=(("en", "English"), ("fr", "French")))
    def test_update_user_invalid_language(self):
        self.client.force_login(self.USER_REGULAR)

        r = self.run_query(
            """
                mutation updateUser($input: UpdateUserInput!) {
                    updateUser(input: $input) {
                        success
                        errors
                        user {
                            id
                            language
                        }
                    }
                }
            """,
            {"input": {"language": "nl"}},
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["INVALID_LANGUAGE"],
                "user": None,
            },
            r["data"]["updateUser"],
        )


class RegisterTest(GraphQLTestCase):
    @classmethod
    def setUp(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "regular",
        )
        cls.WORKSPACE = Workspace.objects.create(name="Workspace")
        cls.WORKSPACE_INVITATION = WorkspaceInvitation.objects.create(
            workspace=cls.WORKSPACE,
            email="johndoe@email.com",
            role=WorkspaceMembershipRole.EDITOR,
        )

        cls.ORGANIZATION = Organization.objects.create(name="Test Organization")
        cls.ORG_OWNER = User.objects.create_user("owner@test.com", "ownerpass")
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_OWNER,
            role=OrganizationMembershipRole.OWNER,
        )
        cls.ORG_INVITATION = OrganizationInvitation.objects.create(
            organization=cls.ORGANIZATION,
            email="orginvitee@email.com",
            role=OrganizationMembershipRole.MEMBER,
            invited_by=cls.ORG_OWNER,
        )

        cls.SIGNUP_REQUEST = SignupRequest.objects.create(
            email="selfregister@email.com"
        )

    def test_register_invalid_token(self):
        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "Pa$$Word",
                    "password2": "Pa$$Word",
                    "firstName": "John",
                    "lastName": "Doe",
                    "invitationToken": "zdzd",
                }
            },
        )

        self.assertEqual(
            r["data"]["register"], {"success": False, "errors": ["INVALID_TOKEN"]}
        )

    def test_register_password_mismatch(self):
        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "Pa$$Word",
                    "password2": "Pa$$Word2",
                    "firstName": "John",
                    "lastName": "Doe",
                    "invitationToken": self.WORKSPACE_INVITATION.generate_token(),
                }
            },
        )

        self.assertEqual(
            r["data"]["register"], {"success": False, "errors": ["PASSWORD_MISMATCH"]}
        )

    def test_register_ok(self):
        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "Pa$$Word1",
                    "password2": "Pa$$Word1",
                    "firstName": "John",
                    "lastName": "Doe",
                    "invitationToken": self.WORKSPACE_INVITATION.generate_token(),
                }
            },
        )

        self.assertTrue(r["data"]["register"]["success"])

        # Check if authenticated
        r = self.run_query(
            """
            query {
                me {
                    user {
                        id
                        firstName
                        lastName
                        email
                    }
                }
            }
            """,
        )

        self.assertEqual(
            r["data"]["me"]["user"],
            {
                "id": str(User.objects.get(email=self.WORKSPACE_INVITATION.email).id),
                "firstName": "John",
                "lastName": "Doe",
                "email": self.WORKSPACE_INVITATION.email,
            },
        )

    def test_register_with_organization_invitation(self):
        """Test registration using an organization invitation token."""
        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "Pa$$Word1",
                    "password2": "Pa$$Word1",
                    "firstName": "Org",
                    "lastName": "Invitee",
                    "invitationToken": self.ORG_INVITATION.generate_token(),
                }
            },
        )

        self.assertTrue(r["data"]["register"]["success"])

        user = User.objects.get(email=self.ORG_INVITATION.email)
        self.assertEqual(user.first_name, "Org")
        self.assertEqual(user.last_name, "Invitee")

        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=user, organization=self.ORGANIZATION
            ).exists()
        )
        self.ORG_INVITATION.refresh_from_db()
        self.assertEqual(
            self.ORG_INVITATION.status, OrganizationInvitationStatus.ACCEPTED
        )

    def test_register_with_signup_request(self):
        """Test registration using a self-registration signup request token."""
        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "Pa$$Word1",
                    "password2": "Pa$$Word1",
                    "firstName": "Self",
                    "lastName": "Register",
                    "invitationToken": self.SIGNUP_REQUEST.generate_token(),
                }
            },
        )

        self.assertTrue(r["data"]["register"]["success"])

        user = User.objects.get(email=self.SIGNUP_REQUEST.email)
        self.assertEqual(user.first_name, "Self")
        self.assertEqual(user.last_name, "Register")

        self.assertFalse(OrganizationMembership.objects.filter(user=user).exists())

        self.SIGNUP_REQUEST.refresh_from_db()
        self.assertEqual(self.SIGNUP_REQUEST.status, SignupRequestStatus.ACCEPTED)

    def test_register_already_logged_in(self):
        """Test that already logged-in users cannot register."""
        self.client.force_login(self.USER_REGULAR)
        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "Pa$$Word1",
                    "password2": "Pa$$Word1",
                    "firstName": "New",
                    "lastName": "User",
                    "invitationToken": self.SIGNUP_REQUEST.generate_token(),
                }
            },
        )

        self.assertEqual(
            r["data"]["register"], {"success": False, "errors": ["ALREADY_LOGGED_IN"]}
        )

    def test_register_email_taken(self):
        """Test registration fails when email is already taken."""
        existing_email_request = SignupRequest.objects.create(
            email=self.USER_REGULAR.email
        )

        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "Pa$$Word1",
                    "password2": "Pa$$Word1",
                    "firstName": "John",
                    "lastName": "Doe",
                    "invitationToken": existing_email_request.generate_token(),
                }
            },
        )

        self.assertEqual(
            r["data"]["register"], {"success": False, "errors": ["EMAIL_TAKEN"]}
        )

    def test_register_invalid_password(self):
        """Test registration fails with invalid password."""
        r = self.run_query(
            """
            mutation register($input: RegisterInput!) {
                register(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "password1": "short",
                    "password2": "short",
                    "firstName": "Self",
                    "lastName": "Register",
                    "invitationToken": self.SIGNUP_REQUEST.generate_token(),
                }
            },
        )

        self.assertEqual(
            r["data"]["register"], {"success": False, "errors": ["INVALID_PASSWORD"]}
        )


class SignupTest(GraphQLTestCase):
    """Tests for the self-registration signup mutation."""

    @classmethod
    def setUp(cls):
        cls.USER_EXISTING = User.objects.create_user(
            "existing@email.com",
            "existingpass",
        )

    @override_settings(ALLOW_SELF_REGISTRATION=True)
    @patch("hexa.user_management.schema.send_signup_email")
    def test_signup_success(self, mock_send_email):
        """Test successful signup request."""
        r = self.run_query(
            """
            mutation signup($input: SignupInput!) {
                signup(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"email": "newuser@email.com"}},
        )

        self.assertEqual(r["data"]["signup"], {"success": True, "errors": []})

        signup_request = SignupRequest.objects.get(email="newuser@email.com")
        self.assertEqual(signup_request.status, SignupRequestStatus.PENDING)
        mock_send_email.assert_called_once()

    @override_settings(ALLOW_SELF_REGISTRATION=False)
    def test_signup_self_registration_disabled(self):
        """Test signup fails when self-registration is disabled."""
        r = self.run_query(
            """
            mutation signup($input: SignupInput!) {
                signup(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"email": "newuser@email.com"}},
        )

        self.assertEqual(
            r["data"]["signup"],
            {"success": False, "errors": ["SELF_REGISTRATION_DISABLED"]},
        )

    @override_settings(ALLOW_SELF_REGISTRATION=True)
    def test_signup_email_taken(self):
        """Test signup returns success even when email is already taken (to prevent email enumeration)."""
        r = self.run_query(
            """
            mutation signup($input: SignupInput!) {
                signup(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"email": self.USER_EXISTING.email}},
        )

        # Returns success to prevent email enumeration attacks
        self.assertEqual(r["data"]["signup"], {"success": True, "errors": []})

    @override_settings(ALLOW_SELF_REGISTRATION=True)
    @patch("hexa.user_management.schema.send_signup_email")
    def test_signup_existing_pending_request(self, mock_send_email):
        """Test signup with existing pending request resends email."""
        existing_request = SignupRequest.objects.create(email="pending@email.com")

        r = self.run_query(
            """
            mutation signup($input: SignupInput!) {
                signup(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"email": "pending@email.com"}},
        )

        self.assertEqual(r["data"]["signup"], {"success": True, "errors": []})

        self.assertEqual(
            SignupRequest.objects.filter(email="pending@email.com").count(), 1
        )
        mock_send_email.assert_called_once()
        called_request = mock_send_email.call_args[0][0]
        self.assertEqual(called_request.id, existing_request.id)

    @override_settings(ALLOW_SELF_REGISTRATION=True)
    @patch("hexa.user_management.schema.send_signup_email")
    def test_signup_email_normalized(self, mock_send_email):
        """Test that email is normalized (lowercase, trimmed)."""
        r = self.run_query(
            """
            mutation signup($input: SignupInput!) {
                signup(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"email": "  NewUser@Email.Com  "}},
        )

        self.assertEqual(r["data"]["signup"], {"success": True, "errors": []})

        signup_request = SignupRequest.objects.get(email="newuser@email.com")
        self.assertIsNotNone(signup_request)
