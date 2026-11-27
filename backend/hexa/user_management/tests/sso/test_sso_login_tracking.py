from unittest.mock import patch

from allauth.account.signals import user_logged_in
from django.test import RequestFactory, TestCase

from hexa.user_management.models import User


class SSOLoginTrackingTest(TestCase):
    """SSO logins bypass the login mutation, so they must be tracked on allauth's signal."""

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

    def sso_login(self, user):
        request = RequestFactory().get("/")
        request.user = user
        user_logged_in.send(sender=User, request=request, user=user)
        return request

    @patch("hexa.user_management.sso.signals.track")
    def test_sso_login_without_two_factor_is_tracked(self, mock_track):
        request = self.sso_login(self.USER_WITHOUT_DEVICE)

        mock_track.assert_called_once_with(
            request, "users.user_logged_in", user=self.USER_WITHOUT_DEVICE
        )

    @patch("hexa.user_management.sso.signals.track")
    def test_sso_login_with_pending_two_factor_is_not_tracked(self, mock_track):
        # The login is only complete once the OTP is verified, so verifyTwoFactorLogin
        # tracks it instead (see test_sso_two_factor.test_valid_code_tracks_login).
        self.sso_login(self.USER_WITH_DEVICE)

        mock_track.assert_not_called()
