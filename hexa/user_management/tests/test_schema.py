import re
from unittest.mock import patch

from django.core import mail
from django.utils.http import urlsafe_base64_encode

from hexa.core.test import GraphQLTestCase
from hexa.core.test.utils import graphql_datetime_format
from hexa.user_management.models import (
    Feature,
    FeatureFlag,
    Membership,
    MembershipRole,
    Team,
    User,
)


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
            feature=cls.FEATURE, user=cls.USER_TAYLOR, config={"config_argument": 10}
        )

    def test_me_anonymous(self):
        r = self.run_query(
            """
              query {
                me {
                  user {
                    id
                  }
                  authorizedActions
                  features {
                    code
                  }
                }
              }
            """,
        )

        self.assertEqual(
            {"user": None, "authorizedActions": [], "features": []},
            r["data"]["me"],
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
                  authorizedActions
                  features {
                    code
                    config
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
                    "lastLogin": graphql_datetime_format(self.USER_JIM.last_login)
                    if self.USER_JIM.last_login
                    else None,
                },
                "features": [],
                "authorizedActions": ["CREATE_TEAM", "CREATE_ACCESSMOD_PROJECT"],
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
                    config
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
                        "config": self.TAYLOR_FEATURE_FLAG.config,
                    }
                ],
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
              query team($id: String!) {
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
              query team($id: String!) {
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

    def test_login(self):
        r = self.run_query(
            """
              mutation login($input: LoginInput!) {
                login(input: $input) {
                  success
                  me {
                    user {
                      id
                    }
                  }
                }
              }
            """,
            {"input": {"email": "jim@bluesquarehub.com", "password": "jimspassword"}},
        )

        self.assertEqual(
            {"success": True, "me": {"user": {"id": str(self.USER_JIM.id)}}},
            r["data"]["login"],
        )

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
        self.assertEqual(mail.outbox[0].subject, "Password reset on localhost:3000")

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
                    "uidb64": urlsafe_base64_encode("2".encode()),
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
                authorizedActions
              }
            }
          """,
        )

        self.assertEqual(
            {
                "user": {
                    "id": str(self.USER_STAFF_NICO.id),
                },
                "authorizedActions": [
                    "CREATE_TEAM",
                    "ADMIN_PANEL",
                    "CREATE_ACCESSMOD_PROJECT",
                ],
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
                authorizedActions
              }
            }
          """,
        )

        self.assertEqual(
            {
                "user": {
                    "id": str(self.SUPER_USER_ALF.id),
                },
                "authorizedActions": [
                    "CREATE_TEAM",
                    "ADMIN_PANEL",
                    "SUPER_USER",
                    "CREATE_ACCESSMOD_PROJECT",
                    "MANAGE_ACCESSMOD_ACCESS_REQUESTS",
                ],
            },
            r["data"]["me"],
        )
