import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest

from hexa.core.utils import get_email_attachments, send_mail
from hexa.user_management.models import User

logger = logging.getLogger(__name__)


class OpenHexaSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request: HttpRequest, sociallogin: SocialLogin) -> None:
        # Allauth stores state["next"] as the post-login redirect URL.  If it's a
        # relative path, Django would redirect the browser to the backend (port 8000)
        # instead of the Next.js frontend (port 3000).  Prefix with the frontend
        # domain so the browser lands on the right page.
        next_url = sociallogin.state.get("next", "")
        if (
            next_url
            and not next_url.startswith(("http://", "https://"))
            and settings.NEW_FRONTEND_DOMAIN
        ):
            sociallogin.state[
                "next"
            ] = f"{settings.NEW_FRONTEND_DOMAIN.rstrip('/')}{next_url}"

        if sociallogin.is_existing:
            return

        # Only link/create accounts when the provider has verified the email.
        # Defaults to True when the claim is absent (Entra ID verifies at IdP level
        # and often omits the field entirely).
        if not sociallogin.account.extra_data.get("email_verified", True):
            return

        email = (sociallogin.account.extra_data.get("email") or "").strip().lower()
        if not email:
            return

        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def is_auto_signup_allowed(
        self, request: HttpRequest, sociallogin: SocialLogin
    ) -> bool:
        data = sociallogin.account.extra_data
        email = (data.get("email") or "").strip()
        email_verified = data.get("email_verified", True)
        return bool(email and email_verified)

    def save_user(
        self, request: HttpRequest, sociallogin: SocialLogin, form: object | None = None
    ) -> User:
        """Create a new OpenHEXA user from the OIDC claims."""
        data = sociallogin.account.extra_data
        email = (data.get("email") or "").strip().lower()
        if not email:
            raise ValueError(
                f"OIDC provider {sociallogin.account.provider!r} did not supply an email address"
            )

        first_name = (data.get("given_name") or data.get("first_name") or "").strip()
        last_name = (data.get("family_name") or data.get("last_name") or "").strip()

        with transaction.atomic():
            user = User(email=email, first_name=first_name, last_name=last_name)
            user.set_unusable_password()
            user.save()

            sociallogin.user = user
            sociallogin.save(request)

        try:
            self._send_new_account_email(user, sociallogin.account.provider)
        except Exception:
            logger.exception(
                "Failed to send SSO new-account notification for %s (provider: %s)",
                user.email,
                sociallogin.account.provider,
            )

        return user

    def _send_new_account_email(self, user: User, provider_id: str) -> None:
        provider_config = next(
            (p for p in settings.OIDC_PROVIDERS if p["id"] == provider_id),
            None,
        )
        if not provider_config:
            return
        recipients = provider_config.get("new_account_email_recipients", [])
        if not recipients:
            return

        display_name = provider_config.get("display_name", provider_id.upper())
        send_mail(
            title=f"New OpenHEXA account created via {display_name}",
            recipient_list=recipients,
            template_name="user_management/mails/sso_new_account",
            template_variables={
                "new_user": user,
                "provider_name": display_name,
            },
            attachments=get_email_attachments(),
        )
