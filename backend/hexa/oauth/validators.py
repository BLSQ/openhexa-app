from django.conf import settings
from oauth2_provider.oauth2_validators import OAuth2Validator

ALLOWED_GRANT_TYPES = {"authorization_code", "refresh_token"}


class OpenHEXAOAuth2Validator(OAuth2Validator):
    """Gives git credential tokens a long lifetime so the helper rarely refreshes.

    Git Credential Manager doesn't reliably refresh expired tokens, so a short
    lifetime makes its first request after expiry fail. MCP/other clients keep
    the short default.

    Only the authorization code and refresh token grants are accepted, whatever
    the application is configured with: the others (e.g. password) mint tokens
    without going through the login flow and its 2FA check.
    """

    def validate_grant_type(
        self, client_id, grant_type, client, request, *args, **kwargs
    ):
        if grant_type not in ALLOWED_GRANT_TYPES:
            return False
        return super().validate_grant_type(
            client_id, grant_type, client, request, *args, **kwargs
        )

    def save_bearer_token(self, token, request, *args, **kwargs):
        client = getattr(request, "client", None)
        client_id = getattr(client, "client_id", None)
        if client_id in settings.GIT_OAUTH_CLIENT_IDS and "expires_in" in token:
            token["expires_in"] = settings.GIT_ACCESS_TOKEN_EXPIRE_SECONDS
        return super().save_bearer_token(token, request, *args, **kwargs)
