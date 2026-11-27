from django.http import HttpRequest

from hexa.analytics.api import track
from hexa.user_management.models import User
from hexa.user_management.utils import has_configured_two_factor


def track_sso_login(request: HttpRequest, user: User, **kwargs):
    """Track SSO logins, which go through allauth instead of the login mutation.

    Users with 2FA are tracked once they complete it in verifyTwoFactorLogin, as SSO
    never verifies their OTP device.
    """
    if not has_configured_two_factor(user):
        track(request, "users.user_logged_in", user=user)
