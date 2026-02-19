import inspect
import json
import logging

from hexa.core.graphql import result_page

logger = logging.getLogger(__name__)

MCP_SERVER_NAME = "OpenHEXA"
MCP_SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2025-03-26"

_TOOLS = {}


def tool(func):
    _TOOLS[func.__name__] = func
    return func


def _page_response(queryset, page: int = 1, per_page: int = 10):
    result = result_page(queryset, page=page, per_page=per_page)
    return {
        "page_number": result["page_number"],
        "total_pages": result["total_pages"],
        "total_items": result["total_items"],
        "items": [_serialize(item) for item in result["items"]],
    }


def _serialize(obj):
    from hexa.datasets.models import Dataset
    from hexa.pipelines.models import Pipeline
    from hexa.workspaces.models import Workspace

    if isinstance(obj, Workspace):
        return {
            "slug": obj.slug,
            "name": obj.name,
            "description": obj.description or "",
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
        }
    elif isinstance(obj, Pipeline):
        return {
            "id": str(obj.id),
            "code": obj.code,
            "name": obj.name or "",
            "description": obj.description or "",
            "workspace_slug": obj.workspace.slug if obj.workspace else None,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
        }
    elif isinstance(obj, Dataset):
        return {
            "id": str(obj.id),
            "slug": obj.slug,
            "name": obj.name or "",
            "description": obj.description or "",
            "workspace_slug": obj.workspace.slug if obj.workspace else None,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
        }
    return str(obj)


def _get_tool_schema(func):
    sig = inspect.signature(func)
    properties = {}
    required = []

    type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}

    for name, param in sig.parameters.items():
        if name == "user":
            continue
        annotation = param.annotation
        prop = {"type": type_map.get(annotation, "string")}
        if param.default is inspect.Parameter.empty:
            required.append(name)
        properties[name] = prop

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def get_tools_list():
    tools = []
    for name, func in _TOOLS.items():
        tools.append(
            {
                "name": name,
                "description": func.__doc__ or "",
                "inputSchema": _get_tool_schema(func),
            }
        )
    return tools


def call_tool(name, arguments, user):
    func = _TOOLS.get(name)
    if not func:
        raise ValueError(f"Unknown tool: {name}")
    arguments["user"] = user
    return func(**arguments)


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
            content = json.dumps(result) if not isinstance(result, str) else result
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": content}],
                },
            }
        except Exception as e:
            logger.exception("Tool call failed: %s", tool_name)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": str(e)}],
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


@tool
def list_workspaces(
    user,
    query: str = "",
    page: int = 1,
    per_page: int = 10,
) -> dict:
    """List workspaces accessible to the current user. Optionally filter by name."""
    from hexa.workspaces.models import Workspace

    qs = Workspace.objects.filter_for_user(user)
    if query:
        qs = qs.filter(name__icontains=query)
    return _page_response(qs, page=page, per_page=per_page)


@tool
def get_workspace(user, slug: str) -> dict:
    """Get details of a specific workspace by its slug."""
    from hexa.workspaces.models import Workspace

    try:
        workspace = Workspace.objects.filter_for_user(user).get(slug=slug)
        return _serialize(workspace)
    except Workspace.DoesNotExist:
        return {"error": "Workspace not found"}


@tool
def list_pipelines(
    user,
    workspace_slug: str,
    page: int = 1,
    per_page: int = 10,
) -> dict:
    """List pipelines in a workspace."""
    from hexa.pipelines.models import Pipeline

    qs = Pipeline.objects.filter_for_user(user).filter(workspace__slug=workspace_slug)
    return _page_response(qs, page=page, per_page=per_page)


@tool
def list_datasets(
    user,
    workspace_slug: str,
    page: int = 1,
    per_page: int = 10,
) -> dict:
    """List datasets in a workspace."""
    from hexa.datasets.models import Dataset

    qs = Dataset.objects.filter_for_user(user).filter(workspace__slug=workspace_slug)
    return _page_response(qs, page=page, per_page=per_page)


@tool
def list_files(
    user,
    workspace_slug: str,
    prefix: str = "",
    page: int = 1,
    per_page: int = 30,
) -> dict:
    """List files and directories in a workspace bucket. Use prefix to browse subdirectories (e.g. "data/")."""
    from hexa.files import storage

    try:
        workspace = _get_workspace_for_user(user, workspace_slug)
    except Exception:
        return {"error": "Workspace not found"}

    if not user.has_perm("files.download_object", workspace):
        return {"error": "Permission denied"}

    try:
        result = storage.list_bucket_objects(
            workspace.bucket_name, prefix=prefix or None, page=page, per_page=per_page
        )
    except Exception:
        return {"error": "Failed to list files"}

    items = [
        {
            "name": obj.name,
            "key": str(obj.key),
            "type": obj.type,
            "size": obj.size,
            "content_type": obj.content_type,
            "updated_at": obj.updated_at.isoformat()
            if hasattr(obj.updated_at, "isoformat")
            else obj.updated_at,
        }
        for obj in result.items
    ]
    return {
        "page_number": result.page_number,
        "has_next_page": result.has_next_page,
        "has_previous_page": result.has_previous_page,
        "items": items,
    }


MAX_READ_SIZE = 1 * 1024 * 1024  # 1 MB


def _get_workspace_for_user(user, workspace_slug: str):
    from hexa.workspaces.models import Workspace

    return Workspace.objects.filter_for_user(user).get(slug=workspace_slug)


def _read_file_content(bucket_name: str, file_path: str) -> bytes:
    from hexa.files import storage

    if storage.storage_type == "local":
        full_path = storage.path(bucket_name, file_path)
        with open(full_path, "rb") as f:
            return f.read()
    elif storage.storage_type == "gcp":
        blob = storage.client.bucket(bucket_name).blob(file_path)
        return blob.download_as_bytes()
    else:
        raise ValueError(f"Unsupported storage type: {storage.storage_type}")


@tool
def read_file(user, workspace_slug: str, file_path: str) -> dict:
    """Read the content of a file from a workspace bucket. The file must be smaller than 1 MB and valid UTF-8 text."""
    from hexa.files import storage

    try:
        workspace = _get_workspace_for_user(user, workspace_slug)
    except Exception:
        return {"error": "Workspace not found"}

    if not user.has_perm("files.download_object", workspace):
        return {"error": "Permission denied"}

    try:
        obj = storage.get_bucket_object(workspace.bucket_name, file_path)
    except Exception:
        return {"error": f"File not found: {file_path}"}

    if obj.type != "file":
        return {"error": f"{file_path} is a directory, not a file"}

    if obj.size > MAX_READ_SIZE:
        return {
            "error": f"File too large ({obj.size} bytes). Maximum is {MAX_READ_SIZE} bytes."
        }

    try:
        content = _read_file_content(workspace.bucket_name, file_path)
        return {"content": content.decode("utf-8"), "size": len(content)}
    except UnicodeDecodeError:
        return {"error": "File is not valid UTF-8 text"}


@tool
def write_file(user, workspace_slug: str, file_path: str, content: str) -> dict:
    """Write text content to a file in a workspace bucket. Creates or overwrites the file at the given path."""
    import io

    from hexa.files import storage

    try:
        workspace = _get_workspace_for_user(user, workspace_slug)
    except Exception:
        return {"error": "Workspace not found"}

    if not user.has_perm("files.create_object", workspace):
        return {"error": "Permission denied"}

    encoded = content.encode("utf-8")
    storage.save_object(workspace.bucket_name, file_path, io.BytesIO(encoded))
    return {"success": True, "file_path": file_path, "size": len(encoded)}


@tool
def get_dataset(user, workspace_slug: str, dataset_slug: str) -> dict:
    """Get details of a specific dataset by workspace slug and dataset slug."""
    from hexa.datasets.models import Dataset

    try:
        dataset = (
            Dataset.objects.filter_for_user(user)
            .filter(workspace__slug=workspace_slug)
            .get(slug=dataset_slug)
        )
        return _serialize(dataset)
    except Dataset.DoesNotExist:
        return {"error": "Dataset not found"}
