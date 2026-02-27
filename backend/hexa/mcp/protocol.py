import inspect
import json
import logging

from hexa.mcp.models import ToolCall

logger = logging.getLogger(__name__)

MCP_SERVER_NAME = "OpenHEXA"
MCP_SERVER_VERSION = "0.0.1"
PROTOCOL_VERSION = "2025-03-26"

_TOOLS = {}


def tool(func):
    _TOOLS[func.__name__] = func
    return func


def _get_tool_schema(func):
    sig = inspect.signature(func)
    properties = {}
    required = []
    type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}

    for name, param in sig.parameters.items():
        if name == "user":
            continue
        properties[name] = {"type": type_map.get(param.annotation, "string")}
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {"type": "object", "properties": properties, "required": required}


def get_tools_list():
    return [
        {
            "name": name,
            "description": func.__doc__ or "",
            "inputSchema": _get_tool_schema(func),
        }
        for name, func in _TOOLS.items()
    ]


def call_tool(name, arguments, user):
    func = _TOOLS.get(name)
    if not func:
        raise ValueError(f"Unknown tool: {name}")
    try:
        result = func(user=user, **arguments)
        ToolCall.objects.create(
            user=user, tool_name=name, arguments=arguments, success=True
        )
        return result
    except Exception as e:
        ToolCall.objects.create(
            user=user, tool_name=name, arguments=arguments, success=False, error=str(e)
        )
        raise


def handle_jsonrpc(body: bytes, user) -> dict | None:
    try:
        request = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None,
        }

    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": MCP_SERVER_NAME, "version": MCP_SERVER_VERSION},
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": get_tools_list()},
        }

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            result = call_tool(tool_name, tool_args, user)
            content = (
                json.dumps(result, default=str)
                if not isinstance(result, str)
                else result
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": content}],
                },
            }
        except Exception:
            logger.exception("Tool call failed: %s", tool_name)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "An internal error occurred while running the tool.",
                        }
                    ],
                    "isError": True,
                },
            }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }
