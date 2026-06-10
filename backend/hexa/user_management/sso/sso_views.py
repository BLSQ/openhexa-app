from django.http import Http404, HttpRequest

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView, OAuth2LoginView
from allauth.socialaccount.providers.openid_connect.views import OpenIDConnectOAuth2Adapter
from allauth.utils import build_absolute_uri


class _FixedCallbackAdapter(OpenIDConnectOAuth2Adapter):
    """Adapter that advertises a configured path as the redirect_uri.

    Used when the IdP has a legacy redirect_uri registered at a non-standard
    path (e.g. from a previous app at the same domain) and we want to honour
    that registration without asking the IdP admin to add a new one.
    """

    def __init__(self, request: HttpRequest, provider_id: str, callback_path: str) -> None:
        super().__init__(request, provider_id)
        self._callback_path = callback_path

    def get_callback_url(self, request: HttpRequest, app) -> str:
        path = "/" + self._callback_path.lstrip("/")
        return build_absolute_uri(request, path, self.redirect_uri_protocol)


def make_compat_login_view(provider_id: str, callback_path: str):
    """Return a login view that sends callback_path as the redirect_uri."""

    @login_not_required
    def compat_login(request: HttpRequest):
        try:
            adapter = _FixedCallbackAdapter(request, provider_id, callback_path)
            view = OAuth2LoginView.adapter_view(adapter)
            return view(request)
        except SocialApp.DoesNotExist:
            raise Http404

    return compat_login


def make_compat_callback_view(provider_id: str, callback_path: str):
    """Return a callback view that handles the OIDC redirect at callback_path."""

    @login_not_required
    def compat_callback(request: HttpRequest):
        try:
            adapter = _FixedCallbackAdapter(request, provider_id, callback_path)
            view = OAuth2CallbackView.adapter_view(adapter)
            return view(request)
        except SocialApp.DoesNotExist:
            raise Http404

    return compat_callback
