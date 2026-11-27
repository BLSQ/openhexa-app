from django.contrib import admin

from hexa.app import CoreAppConfig


class UserManagementConfig(CoreAppConfig):
    name = "hexa.user_management"
    label = "user_management"

    verbose_name = "User management"

    def ready(self):
        super().ready()
        self._unregister_unused_allauth_admin()
        self._connect_sso_login_tracking()

    @staticmethod
    def _connect_sso_login_tracking():
        from allauth.account.signals import user_logged_in

        from hexa.user_management.sso.signals import track_sso_login

        user_logged_in.connect(track_sso_login, dispatch_uid="track_sso_login")

    @staticmethod
    def _unregister_unused_allauth_admin():
        """Hide allauth models that are unused or auto-managed in our SSO setup
        (only SocialAccount stays registered).

        Must run in ready(), after admin autodiscovery has imported allauth's
        admin modules.
        """
        from allauth.account.models import EmailAddress, EmailConfirmation
        from allauth.socialaccount.models import SocialApp, SocialToken

        for model in (EmailAddress, EmailConfirmation, SocialApp, SocialToken):
            if admin.site.is_registered(model):
                admin.site.unregister(model)

    ANONYMOUS_URLS = [
        "logout",
        "password_reset",
        "password_reset_confirm",
        "password_reset_done",
        "password_reset_complete",
        "openid_connect_login",
        "openid_connect_callback",
        "socialaccount_signup",
        "socialaccount_login_error",
        "socialaccount_login_cancelled",
    ]
