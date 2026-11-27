"""OAuth scope names, shared by the authorization views and the token validator."""

GIT_SCOPE = "openhexa:git"
MCP_SCOPE = "openhexa:mcp"

# Issued by the server itself to a workspace copy run, never through the
# authorization flow: it is left out of OAUTH2_PROVIDER["SCOPES"] so no OAuth
# client can request it.
WORKSPACE_COPY_SCOPE = "openhexa:workspace_copy"
