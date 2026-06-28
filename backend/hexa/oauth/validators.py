from django.conf import settings
from oauth2_provider.oauth2_validators import OAuth2Validator


class OpenHEXAOAuth2Validator(OAuth2Validator):
    """Gives git credential tokens a long lifetime so the helper rarely refreshes.

    Git Credential Manager doesn't reliably refresh expired tokens, so a short
    lifetime makes its first request after expiry fail. MCP/other clients keep
    the short default.
    """

    def save_bearer_token(self, token, request, *args, **kwargs):
        client = getattr(request, "client", None)
        client_id = getattr(client, "client_id", None)
        if client_id in settings.GIT_OAUTH_CLIENT_IDS and "expires_in" in token:
            token["expires_in"] = settings.GIT_ACCESS_TOKEN_EXPIRE_SECONDS
        return super().save_bearer_token(token, request, *args, **kwargs)
