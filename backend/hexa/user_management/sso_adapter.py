from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.http import HttpRequest

from hexa.user_management.models import User


class OpenHexaSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request: HttpRequest, sociallogin: SocialLogin) -> None:
        """Auto-link an incoming OIDC identity to an existing OpenHEXA user by email."""
        if sociallogin.is_existing:
            return

        email = (sociallogin.account.extra_data.get("email") or "").strip().lower()
        if not email:
            return

        try:
            user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def is_auto_signup_allowed(
        self, request: HttpRequest, sociallogin: SocialLogin
    ) -> bool:
        return True

    def save_user(
        self, request: HttpRequest, sociallogin: SocialLogin, form: object | None = None
    ) -> User:
        """Create a new OpenHEXA user from the OIDC claims."""
        data = sociallogin.account.extra_data
        email = (data.get("email") or "").strip().lower()
        first_name = (data.get("given_name") or data.get("first_name") or "").strip()
        last_name = (data.get("family_name") or data.get("last_name") or "").strip()

        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_unusable_password()
        user.save()

        sociallogin.user = user
        sociallogin.save(request)
        return user

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        return request.GET.get("next") or "/"
