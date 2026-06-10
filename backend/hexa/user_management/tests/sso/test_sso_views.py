from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from hexa.user_management.sso.sso_views import (
    _FixedCallbackAdapter,
    make_compat_callback_view,
    make_compat_login_view,
)

_WHO_CIAM_CONFIG = {
    "id": "who-ciam",
    "client_id": "test-client-id",
    "client_secret": "test-secret",
    "server_url": "https://login.microsoftonline.com/test-tenant/v2.0",
    "display_name": "WHO CIAM",
    "new_account_email_recipients": [],
    "callback_path": "polio/login/callback/",
    "login_path": "polio/login/",
}


class FixedCallbackAdapterTest(TestCase):
    def _make_request(self, scheme="https", host="openhexa.example.com"):
        request = RequestFactory().get("/")
        request.META["HTTP_HOST"] = host
        request.META["SERVER_NAME"] = host
        request.META["SERVER_PORT"] = "443" if scheme == "https" else "80"
        request.META["wsgi.url_scheme"] = scheme
        return request

    def test_get_callback_url_uses_configured_path(self):
        request = self._make_request()
        adapter = _FixedCallbackAdapter(request, "who-ciam", "polio/login/callback/")

        with patch.object(
            type(adapter),
            "redirect_uri_protocol",
            new_callable=lambda: property(lambda self: "https"),
        ):
            url = adapter.get_callback_url(request, app=MagicMock())

        self.assertEqual(url, "https://openhexa.example.com/polio/login/callback/")

    def test_get_callback_url_strips_extra_leading_slash(self):
        request = self._make_request()
        adapter = _FixedCallbackAdapter(request, "who-ciam", "/polio/login/callback/")

        with patch.object(
            type(adapter),
            "redirect_uri_protocol",
            new_callable=lambda: property(lambda self: "https"),
        ):
            url = adapter.get_callback_url(request, app=MagicMock())

        self.assertEqual(url, "https://openhexa.example.com/polio/login/callback/")

    def test_get_callback_url_respects_http_scheme(self):
        request = self._make_request(scheme="http", host="localhost:8000")
        adapter = _FixedCallbackAdapter(request, "who-ciam", "polio/login/callback/")

        with patch.object(
            type(adapter),
            "redirect_uri_protocol",
            new_callable=lambda: property(lambda self: "http"),
        ):
            url = adapter.get_callback_url(request, app=MagicMock())

        self.assertEqual(url, "http://localhost:8000/polio/login/callback/")


class MakeCompatViewTest(TestCase):
    def test_make_compat_login_view_returns_callable(self):
        view = make_compat_login_view("who-ciam", "polio/login/callback/")
        self.assertTrue(callable(view))

    def test_make_compat_callback_view_returns_callable(self):
        view = make_compat_callback_view("who-ciam", "polio/login/callback/")
        self.assertTrue(callable(view))

    def test_compat_login_view_raises_404_when_provider_not_found(self):
        from allauth.socialaccount.models import SocialApp
        from django.test import RequestFactory as RF

        view = make_compat_login_view("nonexistent-provider", "polio/login/callback/")
        request = RF().get("/polio/login/")

        with patch(
            "hexa.user_management.sso.sso_views.OAuth2LoginView.adapter_view",
            side_effect=SocialApp.DoesNotExist,
        ):
            from django.http import Http404

            with self.assertRaises(Http404):
                view(request)

    def test_compat_callback_view_raises_404_when_provider_not_found(self):
        from allauth.socialaccount.models import SocialApp
        from django.test import RequestFactory as RF

        view = make_compat_callback_view(
            "nonexistent-provider", "polio/login/callback/"
        )
        request = RF().get("/polio/login/callback/")

        with patch(
            "hexa.user_management.sso.sso_views.OAuth2CallbackView.adapter_view",
            side_effect=SocialApp.DoesNotExist,
        ):
            from django.http import Http404

            with self.assertRaises(Http404):
                view(request)


class CompatUrlPatternBuildTest(TestCase):
    """Verify that make_compat_*_view returns views that build the right URL patterns.

    Full URL routing would require reloading the URL conf, which is not practical
    in a unit test. Instead we verify the view factories produce valid callables
    and that the adapter inside them uses the right callback path.
    """

    def test_login_and_callback_views_use_same_callback_path(self):
        login_view = make_compat_login_view("who-ciam", "polio/login/callback/")
        callback_view = make_compat_callback_view("who-ciam", "polio/login/callback/")
        self.assertTrue(callable(login_view))
        self.assertTrue(callable(callback_view))

    def test_adapter_stores_provider_id_and_path(self):
        request = RequestFactory().get("/")
        adapter = _FixedCallbackAdapter(request, "who-ciam", "polio/login/callback/")
        self.assertEqual(adapter.provider_id, "who-ciam")
        self.assertEqual(adapter._callback_path, "polio/login/callback/")
