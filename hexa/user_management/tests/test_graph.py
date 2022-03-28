import re

from django.core import mail
from django.utils.http import urlsafe_base64_encode

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User


class UserManagementGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimspassword",
        )

    def test_me_anonymous(self):
        r = self.run_query(
            """
               query {
                  me {
                      id
                  }
                }
            """,
        )

        self.assertEqual(
            None,
            r["data"]["me"],
        )

    def test_me(self):
        self.client.force_login(self.USER)
        r = self.run_query(
            """
               query {
                  me {
                      id
                  }
                }
            """,
        )

        self.assertEqual(
            {"id": str(self.USER.id)},
            r["data"]["me"],
        )


class AuthGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimspassword",
        )

    def test_login(self):
        r = self.run_query(
            """
                mutation login($input: LoginInput!) {
                  login(input: $input) {
                    success
                    me {
                      id
                    }
                  }
                }
            """,
            {"input": {"email": "jim@bluesquarehub.com", "password": "jimspassword"}},
        )

        self.assertEqual(
            {"success": True, "me": {"id": str(self.USER.id)}},
            r["data"]["login"],
        )

    def test_logout(self):
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
                      id
                  }
                }
            """,
        )

        self.assertEqual(
            None,
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
            {"input": {"email": self.USER.email}},
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

    def _test_reset_start(self):
        # Start by creating the email
        self.run_query(
            """
                mutation resetPassword($input: ResetPasswordInput!) {
                  resetPassword(input: $input) {
                    success
                  }
                }
            """,
            {"input": {"email": self.USER.email}},
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
        existing_pwd = self.USER.password

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
        self.USER.refresh_from_db()
        self.assertNotEqual(existing_pwd, self.USER.password)

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
