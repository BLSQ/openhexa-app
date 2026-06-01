from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from hexa.user_management.models import User


class OpenHexaSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
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

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form=None):
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

    def get_login_redirect_url(self, request):
        return request.GET.get("next") or "/"
