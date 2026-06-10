from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from hexa.user_management.models import User
from hexa.user_management.sso_adapter import OpenHexaSocialAccountAdapter

_WHO_CONFIG = {
    "id": "who",
    "client_id": "test-client-id",
    "client_secret": "test-secret",
    "server_url": "https://login.microsoftonline.com/test-tenant/v2.0",
    "display_name": "WHO",
    "new_account_email_recipients": ["admin@example.org"],
}


def _make_sociallogin(
    email, provider_id="who", is_existing=False, extra=None, state=None
):
    account = MagicMock()
    account.provider = provider_id
    account.extra_data = {
        "email": email,
        "given_name": "Jane",
        "family_name": "Doe",
        **(extra or {}),
    }

    sociallogin = MagicMock()
    sociallogin.account = account
    sociallogin.is_existing = is_existing
    sociallogin.state = state if state is not None else {}
    return sociallogin


class PreSocialLoginTest(TestCase):
    def setUp(self):
        self.adapter = OpenHexaSocialAccountAdapter()
        self.request = MagicMock()

    def test_links_to_existing_user_by_email(self):
        user = User.objects.create_user("jane@who.int", "unused-password")
        sociallogin = _make_sociallogin("jane@who.int")

        self.adapter.pre_social_login(self.request, sociallogin)

        sociallogin.connect.assert_called_once_with(self.request, user)

    def test_skips_when_already_existing(self):
        User.objects.create_user("jane@who.int", "unused-password")
        sociallogin = _make_sociallogin("jane@who.int", is_existing=True)

        self.adapter.pre_social_login(self.request, sociallogin)

        sociallogin.connect.assert_not_called()

    def test_skips_when_no_email_in_claims(self):
        sociallogin = _make_sociallogin("", extra={"email": ""})

        self.adapter.pre_social_login(self.request, sociallogin)

        sociallogin.connect.assert_not_called()

    def test_skips_when_no_matching_user(self):
        sociallogin = _make_sociallogin("unknown@who.int")

        self.adapter.pre_social_login(self.request, sociallogin)

        sociallogin.connect.assert_not_called()

    def test_skips_account_link_when_email_not_verified(self):
        User.objects.create_user("jane@who.int", "unused-password")
        sociallogin = _make_sociallogin("jane@who.int", extra={"email_verified": False})

        self.adapter.pre_social_login(self.request, sociallogin)

        sociallogin.connect.assert_not_called()

    def test_links_when_email_verified_claim_absent(self):
        """Providers like Entra ID often omit email_verified; should default to allowed."""
        user = User.objects.create_user("jane@who.int", "unused-password")
        sociallogin = _make_sociallogin("jane@who.int")
        # extra_data has no email_verified key by default in _make_sociallogin

        self.adapter.pre_social_login(self.request, sociallogin)

        sociallogin.connect.assert_called_once_with(self.request, user)

    @override_settings(NEW_FRONTEND_DOMAIN="http://localhost:3000")
    def test_converts_relative_next_url_to_absolute_frontend_url(self):
        sociallogin = _make_sociallogin(
            "unknown@who.int", state={"next": "/workspaces/"}
        )

        self.adapter.pre_social_login(self.request, sociallogin)

        self.assertEqual(sociallogin.state["next"], "http://localhost:3000/workspaces/")

    @override_settings(NEW_FRONTEND_DOMAIN="http://localhost:3000")
    def test_does_not_modify_absolute_next_url(self):
        sociallogin = _make_sociallogin(
            "unknown@who.int", state={"next": "http://localhost:3000/workspaces/"}
        )

        self.adapter.pre_social_login(self.request, sociallogin)

        self.assertEqual(sociallogin.state["next"], "http://localhost:3000/workspaces/")

    def test_handles_missing_next_in_state(self):
        sociallogin = _make_sociallogin("unknown@who.int", state={})

        self.adapter.pre_social_login(self.request, sociallogin)

        self.assertEqual(sociallogin.state, {})


@override_settings(OIDC_PROVIDERS=[_WHO_CONFIG])
class SaveUserTest(TestCase):
    def setUp(self):
        self.adapter = OpenHexaSocialAccountAdapter()
        self.request = MagicMock()

    def test_creates_user_from_oidc_claims(self):
        sociallogin = _make_sociallogin("jane@who.int")

        with patch("hexa.user_management.sso_adapter.send_mail"):
            user = self.adapter.save_user(self.request, sociallogin)

        self.assertEqual(user.email, "jane@who.int")
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Doe")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(User.objects.filter(email="jane@who.int").exists())

    def test_normalises_email_to_lowercase(self):
        sociallogin = _make_sociallogin("Jane.WHO@WHO.INT")

        with patch("hexa.user_management.sso_adapter.send_mail"):
            user = self.adapter.save_user(self.request, sociallogin)

        self.assertEqual(user.email, "jane.who@who.int")

    def test_sends_notification_email_to_configured_recipients(self):
        sociallogin = _make_sociallogin("jane@who.int")

        with patch("hexa.user_management.sso_adapter.send_mail") as mock_send:
            self.adapter.save_user(self.request, sociallogin)

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        self.assertEqual(call_kwargs["recipient_list"], ["admin@example.org"])
        self.assertIn("WHO", call_kwargs["title"])
        self.assertEqual(call_kwargs["template_variables"]["provider_name"], "WHO")
        self.assertEqual(
            call_kwargs["template_variables"]["new_user"].email, "jane@who.int"
        )

    @override_settings(
        OIDC_PROVIDERS=[{**_WHO_CONFIG, "new_account_email_recipients": []}]
    )
    def test_skips_email_when_no_recipients_configured(self):
        sociallogin = _make_sociallogin("jane@who.int")

        with patch("hexa.user_management.sso_adapter.send_mail") as mock_send:
            self.adapter.save_user(self.request, sociallogin)

        mock_send.assert_not_called()

    @override_settings(OIDC_PROVIDERS=[])
    def test_skips_email_when_provider_not_in_settings(self):
        sociallogin = _make_sociallogin("jane@who.int")

        with patch("hexa.user_management.sso_adapter.send_mail") as mock_send:
            self.adapter.save_user(self.request, sociallogin)

        mock_send.assert_not_called()

    def test_raises_when_email_claim_is_missing(self):
        sociallogin = _make_sociallogin("")
        sociallogin.account.extra_data = {"given_name": "Jane", "family_name": "Doe"}

        with self.assertRaises(ValueError):
            self.adapter.save_user(self.request, sociallogin)

        self.assertFalse(User.objects.filter(first_name="Jane").exists())

    def test_user_persisted_even_when_email_notification_fails(self):
        sociallogin = _make_sociallogin("jane@who.int")

        with patch(
            "hexa.user_management.sso_adapter.send_mail",
            side_effect=Exception("SMTP down"),
        ):
            user = self.adapter.save_user(self.request, sociallogin)

        self.assertEqual(user.email, "jane@who.int")
        self.assertTrue(User.objects.filter(email="jane@who.int").exists())

    def test_user_not_persisted_when_sociallogin_save_fails(self):
        sociallogin = _make_sociallogin("jane@who.int")
        sociallogin.save = MagicMock(side_effect=Exception("DB error"))

        with self.assertRaises(Exception):
            self.adapter.save_user(self.request, sociallogin)

        self.assertFalse(User.objects.filter(email="jane@who.int").exists())

    def test_falls_back_to_first_name_last_name_claims(self):
        """Handles providers that use first_name/last_name instead of given_name/family_name."""
        sociallogin = _make_sociallogin(
            "jane@who.int",
            extra={"email": "jane@who.int", "first_name": "Jane", "last_name": "Doe"},
        )
        # Override extra_data to not include given_name/family_name
        sociallogin.account.extra_data = {
            "email": "jane@who.int",
            "first_name": "Jane",
            "last_name": "Doe",
        }

        with patch("hexa.user_management.sso_adapter.send_mail"):
            user = self.adapter.save_user(self.request, sociallogin)

        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Doe")


class IsAutoSignupAllowedTest(TestCase):
    def setUp(self):
        self.adapter = OpenHexaSocialAccountAdapter()
        self.request = MagicMock()

    def test_allowed_when_email_present_and_verified(self):
        sociallogin = _make_sociallogin("jane@who.int", extra={"email_verified": True})
        self.assertTrue(self.adapter.is_auto_signup_allowed(self.request, sociallogin))

    def test_allowed_when_email_verified_claim_absent(self):
        """Entra ID omits email_verified; should default to allowed."""
        sociallogin = _make_sociallogin("jane@who.int")
        self.assertTrue(self.adapter.is_auto_signup_allowed(self.request, sociallogin))

    def test_denied_when_email_not_verified(self):
        sociallogin = _make_sociallogin("jane@who.int", extra={"email_verified": False})
        self.assertFalse(self.adapter.is_auto_signup_allowed(self.request, sociallogin))

    def test_denied_when_email_absent(self):
        sociallogin = _make_sociallogin("")
        self.assertFalse(self.adapter.is_auto_signup_allowed(self.request, sociallogin))
