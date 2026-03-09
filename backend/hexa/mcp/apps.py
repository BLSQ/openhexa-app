from hexa.app import CoreAppConfig


class McpConfig(CoreAppConfig):
    name = "hexa.mcp"
    label = "mcp"
    default_auto_field = "django.db.models.BigAutoField"

    ANONYMOUS_URLS = [
        "mcp_endpoint_no_slash",
        "mcp:mcp_endpoint",
        "dynamic_client_registration",
        "dynamic_client_registration_no_slash",
        "oauth2_provider:token",
        "oauth_token_openid_configuration",
    ]
