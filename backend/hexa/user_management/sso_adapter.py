import logging

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from hexa.core.utils import get_email_attachments, send_mail
from hexa.user_management.models import User

logger = logging.getLogger(__name__)


class OpenHexaSocialAccountAdapter(DefaultSocialAccountAdapter):
    @staticmethod
    def _get_claims(sociallogin: SocialLogin) -> dict:
        # allauth >= 65.11 stores claims under {"userinfo": {...}, "id_token": {...}}.
        # Older versions stored a flat dict.  Mirror allauth's own _pick_data logic.
        raw = sociallogin.account.extra_data
        return raw.get("userinfo") or raw.get("id_token") or raw

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

        data = self._get_claims(sociallogin)
        email = (data.get("email") or "").strip().lower()
        # Defaults to True when the claim is absent (Entra ID verifies at IdP level
        # and often omits the field entirely).
        email_verified = data.get("email_verified", True)

        if not email or not email_verified:
            # Abort the flow immediately rather than falling through to the allauth
            # signup form, which save_user does not support without an email claim.
            # Redirect to the frontend login page rather than allauth's raw error page.
            login_url = reverse("core:login")
            raise ImmediateHttpResponse(HttpResponseRedirect(login_url))

        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def is_auto_signup_allowed(
        self, request: HttpRequest, sociallogin: SocialLogin
    ) -> bool:
        data = self._get_claims(sociallogin)
        email = (data.get("email") or "").strip()
        email_verified = data.get("email_verified", True)
        return bool(email and email_verified)

    def save_user(
        self, request: HttpRequest, sociallogin: SocialLogin, form: object | None = None
    ) -> User:
        """Create a new OpenHEXA user from the OIDC claims."""
        data = self._get_claims(sociallogin)
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
