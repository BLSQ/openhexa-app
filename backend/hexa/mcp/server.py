import hexa.mcp.tools  # noqa: F401 — registers @tool functions

from .protocol import (
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
    PROTOCOL_VERSION,
    get_tools_list,
    handle_jsonrpc,
)

__all__ = [
    "MCP_SERVER_NAME",
    "MCP_SERVER_VERSION",
    "PROTOCOL_VERSION",
    "get_tools_list",
    "handle_jsonrpc",
]
