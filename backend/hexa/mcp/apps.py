from hexa.app import CoreAppConfig


class McpConfig(CoreAppConfig):
    name = "hexa.mcp"
    label = "mcp"

    ANONYMOUS_URLS = [
        "mcp_endpoint_no_slash",
        "mcp:mcp_endpoint",
        "mcp:dynamic_client_registration",
        "mcp:dynamic_client_registration_no_slash",
        "mcp:mcp_oauth_server_metadata",
        "mcp:mcp_protected_resource_metadata",
        "mcp:mcp_openid_configuration",
        "protected_resource_metadata",
        "protected_resource_metadata_mcp",
        "oauth_server_metadata",
        "oauth_server_metadata_mcp",
        "openid_configuration",
        "openid_configuration_mcp",
        "oauth2_authorize",
        "mcp:oauth_login",
        "oauth2_provider:authorize",
        "oauth2_provider:token",
        "oauth_token_openid_configuration",
    ]
