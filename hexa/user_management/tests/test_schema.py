import re

from django.core import mail
from django.utils.http import urlsafe_base64_encode

from hexa.core.test import GraphQLTestCase
from hexa.core.test.utils import graphql_datetime_format
from hexa.user_management.models import Membership, MembershipRole, Team, User


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

    def test_me_anonymous(self):
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
            {"user": None, "authorizedActions": []},
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
                    email
                    dateJoined
                    lastLogin
                  }
                  authorizedActions
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
                    "email": self.USER_JIM.email,
                    "dateJoined": graphql_datetime_format(self.USER_JIM.date_joined),
                    "lastLogin": graphql_datetime_format(self.USER_JIM.last_login),
                },
                "authorizedActions": ["CREATE_TEAM", "CREATE_ACCESSMOD_PROJECT"],
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
        self.assertEqual(mail.outbox[0].subject, "Password reset on app.openhexa.test")

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
