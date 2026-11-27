from unittest.mock import ANY, patch

from django.core import mail
from django.test import Client
from django_otp import devices_for_user

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User

ME_QUERY = """
    query {
        me {
            twoFactorPending
            user {
                email
            }
        }
    }
"""

GENERATE_CHALLENGE_MUTATION = """
    mutation {
        generateChallenge {
            success
            errors
        }
    }
"""

VERIFY_TWO_FACTOR_LOGIN_MUTATION = """
    mutation verifyTwoFactorLogin($input: VerifyTwoFactorLoginInput!) {
        verifyTwoFactorLogin(input: $input) {
            success
            errors
        }
    }
"""


class SSOTwoFactorLoginTest(GraphQLTestCase):
    """An SSO login (e.g. Google) logs the user in without verifying their OTP device,
    so users with 2FA must then complete it with their emailed code.
    """

    client_class = Client

    @classmethod
    def setUpTestData(cls):
        cls.USER_WITH_DEVICE = User.objects.create_user(
            "jane@bluesquarehub.com", "unused-password"
        )
        cls.USER_WITH_DEVICE.emaildevice_set.create(
            name="default", user=cls.USER_WITH_DEVICE
        )
        cls.USER_WITHOUT_DEVICE = User.objects.create_user(
            "jim@bluesquarehub.com", "unused-password"
        )

    def me(self):
        return self.run_query(ME_QUERY)["data"]["me"]

    def send_code(self):
        r = self.run_query(GENERATE_CHALLENGE_MUTATION)
        self.assertEqual(
            {"success": True, "errors": None}, r["data"]["generateChallenge"]
        )
        device = next(devices_for_user(self.USER_WITH_DEVICE))
        return device.token

    def verify(self, token):
        return self.run_query(
            VERIFY_TWO_FACTOR_LOGIN_MUTATION, {"input": {"token": token}}
        )["data"]["verifyTwoFactorLogin"]

    def test_sso_login_with_two_factor_is_pending(self):
        self.client.force_login(self.USER_WITH_DEVICE)

        self.assertEqual({"twoFactorPending": True, "user": None}, self.me())

    def test_sso_login_without_two_factor_is_not_pending(self):
        self.client.force_login(self.USER_WITHOUT_DEVICE)

        self.assertEqual(
            {
                "twoFactorPending": False,
                "user": {"email": self.USER_WITHOUT_DEVICE.email},
            },
            self.me(),
        )

    def test_anonymous_is_not_pending(self):
        self.assertEqual({"twoFactorPending": False, "user": None}, self.me())

    def test_valid_code_completes_login(self):
        self.client.force_login(self.USER_WITH_DEVICE)
        token = self.send_code()
        self.assertEqual(1, len(mail.outbox))

        self.assertEqual({"success": True, "errors": []}, self.verify(token))
        self.assertEqual(
            {
                "twoFactorPending": False,
                "user": {"email": self.USER_WITH_DEVICE.email},
            },
            self.me(),
        )

    @patch("hexa.user_management.schema.mutations.track")
    def test_valid_code_tracks_login(self, mock_track):
        self.client.force_login(self.USER_WITH_DEVICE)
        token = self.send_code()

        self.verify(token)

        mock_track.assert_called_once_with(
            ANY, "users.user_logged_in", user=self.USER_WITH_DEVICE
        )

    @patch("hexa.user_management.schema.mutations.track")
    def test_invalid_code_does_not_track_login(self, mock_track):
        self.client.force_login(self.USER_WITH_DEVICE)
        self.send_code()

        self.verify("000000")

        mock_track.assert_not_called()

    def test_invalid_code_keeps_login_pending(self):
        self.client.force_login(self.USER_WITH_DEVICE)
        self.send_code()

        self.assertEqual(
            {"success": False, "errors": ["INVALID_OTP"]}, self.verify("000000")
        )
        self.assertEqual({"twoFactorPending": True, "user": None}, self.me())

    def test_valid_code_is_refused_right_after_a_wrong_one(self):
        self.client.force_login(self.USER_WITH_DEVICE)
        token = self.send_code()

        self.verify("000000")

        self.assertEqual(
            {"success": False, "errors": ["INVALID_OTP"]}, self.verify(token)
        )
        self.assertEqual({"twoFactorPending": True, "user": None}, self.me())

    def test_user_without_device_gets_no_device_error(self):
        self.client.force_login(self.USER_WITHOUT_DEVICE)

        self.assertEqual(
            {"success": False, "errors": ["NO_DEVICE"]}, self.verify("123456")
        )

    def test_anonymous_cannot_verify(self):
        r = self.run_query(
            VERIFY_TWO_FACTOR_LOGIN_MUTATION, {"input": {"token": "123456"}}
        )

        self.assertIsNone(r["data"])
        self.assertEqual("UNAUTHENTICATED", r["errors"][0]["extensions"]["code"])
