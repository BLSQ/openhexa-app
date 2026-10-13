import enum
import inspect
import json
import logging
import types
import typing
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from hexa.mcp.models import MCPConnection, MCPResource, ToolCall

logger = logging.getLogger(__name__)

MCP_SERVER_NAME = "OpenHEXA"
MCP_SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2025-03-26"

TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean"}

_TOOLS = {}


@dataclass(frozen=True)
class RegisteredTool:
    func: typing.Callable
    resource: str | None
    write: bool


def _group_of(func, ungated: bool) -> str | None:
    if ungated:
        return None
    module = func.__module__.rsplit(".", 1)[-1].upper()
    if module not in MCPResource.values:
        raise ImproperlyConfigured(
            f"{func.__name__} is defined in {func.__module__}, which matches no "
            f"MCPResource group. Add one, move the tool, or pass ungated=True."
        )
    return module


def tool(func=None, *, write: bool = False, ungated: bool = False):
    def register(func):
        _TOOLS[func.__name__] = RegisteredTool(
            func=func, resource=_group_of(func, ungated), write=write
        )
        return func

    return register(func) if func is not None else register


def _refusal_message(name: str, connection: MCPConnection | None) -> str:
    client = (
        f"The OpenHEXA connection for {connection.application.name}"
        if connection is not None
        else "This OpenHEXA connection"
    )
    return (
        f"{client} is not authorized to call {name}. "
        f"The person who authorized it can turn this tool on at "
        f"{settings.NEW_FRONTEND_DOMAIN}/user/account#mcp-connections "
        f"— the change takes effect on the next call, with no need to "
        f"authorize the client again."
    )


def _is_granted(
    name: str, entry: RegisteredTool, connection: MCPConnection | None
) -> bool:
    if entry.resource is None:
        return True
    if connection is None:
        return False
    return connection.allows_tool(name)


def _base_type(annotation):
    """Unwrap Optional/Union annotations (e.g. `int | None`) to the underlying type."""
    if typing.get_origin(annotation) not in (typing.Union, types.UnionType):
        return annotation
    args = [a for a in typing.get_args(annotation) if a is not type(None)]
    if len(args) == 1:
        return args[0]
    return annotation


def _enum_schema(enum_cls):
    values = [member.value for member in enum_cls]
    value_type = type(values[0]) if values else str
    return {"type": TYPE_MAP.get(value_type, "string"), "enum": values}


def _property_schema(annotation):
    """Build the JSON Schema for a single tool argument from its annotation."""
    base = _base_type(annotation)
    if isinstance(base, type) and issubclass(base, enum.Enum):
        return _enum_schema(base)
    if typing.get_origin(base) is list:
        (item,) = typing.get_args(base) or (str,)
        item_base = _base_type(item)
        # Carry the enum constraint onto the array items too (e.g. a list of scopes).
        if isinstance(item_base, type) and issubclass(item_base, enum.Enum):
            return {"type": "array", "items": _enum_schema(item_base)}
        return {"type": "array", "items": {"type": TYPE_MAP.get(item_base, "string")}}
    # Scalars map directly; anything unrecognized (e.g. dict) degrades to string.
    return {"type": TYPE_MAP.get(base, "string")}


def _get_tool_schema(func):
    sig = inspect.signature(func)
    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if name == "user":
            continue
        properties[name] = _property_schema(param.annotation)
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {"type": "object", "properties": properties, "required": required}


def get_tools_list(connection: MCPConnection | None = None):
    """The tools to advertise. Passing no connection returns the full catalogue,
    which is what the public tool list and the consent screen show.
    """
    return [
        {
            "name": name,
            "description": entry.func.__doc__ or "",
            "inputSchema": _get_tool_schema(entry.func),
        }
        for name, entry in _TOOLS.items()
        if connection is None or _is_granted(name, entry, connection)
    ]


def get_tools_catalogue():
    """Every tool with the grant it needs, for the permission editor."""
    return [
        {
            "name": name,
            "description": entry.func.__doc__ or "",
            "resource": entry.resource,
            "write": entry.write,
        }
        for name, entry in _TOOLS.items()
    ]


def call_tool(name, arguments, user, connection: MCPConnection | None):
    entry = _TOOLS.get(name)
    if not entry:
        raise ValueError(f"Unknown tool: {name}")
    if not _is_granted(name, entry, connection):
        message = _refusal_message(name, connection)
        ToolCall.objects.create(
            user=user, tool_name=name, arguments=arguments, success=False, error=message
        )
        raise PermissionDenied(message)
    try:
        result = entry.func(user=user, **arguments)
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
    connection = getattr(user, "connection", None)
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
            "result": {"tools": get_tools_list(connection)},
        }

    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            result = call_tool(tool_name, tool_args, user, connection)
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
        except PermissionDenied as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": str(e)}],
                    "isError": True,
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
