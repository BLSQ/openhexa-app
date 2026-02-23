import io
from pathlib import Path

from django.http import HttpRequest
from graphql import graphql_sync

from config.schema import schema
from hexa.files import storage
from hexa.workspaces.models import Workspace

from .protocol import tool

_QUERIES_PATH = Path(__file__).parent / "graphql" / "queries.graphql"
_QUERIES_SOURCE = _QUERIES_PATH.read_text()


def _execute_graphql(user, operation_name, variables=None):
    request = HttpRequest()
    request.user = user
    request.bypass_two_factor = True

    result = graphql_sync(
        schema,
        _QUERIES_SOURCE,
        context_value={"request": request},
        variable_values=variables or {},
        operation_name=operation_name,
    )
    if result.errors:
        return {"errors": [str(e) for e in result.errors]}
    return result.data


@tool
def list_workspaces(user, query: str = "", page: int = 1, per_page: int = 10) -> dict:
    """List workspaces accessible to the current user. Optionally filter by name."""
    return _execute_graphql(
        user,
        "ListWorkspaces",
        {"query": query or None, "page": page, "perPage": per_page},
    )


@tool
def get_workspace(user, slug: str) -> dict:
    """Get details of a specific workspace by its slug."""
    return _execute_graphql(user, "GetWorkspace", {"slug": slug})


@tool
def list_pipelines(
    user, workspace_slug: str, page: int = 1, per_page: int = 10
) -> dict:
    """List pipelines in a workspace."""
    return _execute_graphql(
        user,
        "ListPipelines",
        {"workspaceSlug": workspace_slug, "page": page, "perPage": per_page},
    )


@tool
def list_datasets(user, workspace_slug: str, page: int = 1, per_page: int = 10) -> dict:
    """List datasets in a workspace."""
    data = _execute_graphql(
        user,
        "ListDatasets",
        {
            "workspaceSlug": workspace_slug,
            "query": None,
            "page": page,
            "perPage": per_page,
        },
    )
    if "errors" in data:
        return data
    workspace = data.get("workspace")
    if workspace is None:
        return {"error": "Workspace not found"}
    page_data = workspace["datasets"]
    page_data["items"] = [item["dataset"] for item in page_data["items"]]
    return {"datasets": page_data}


@tool
def get_dataset(user, workspace_slug: str, dataset_slug: str) -> dict:
    """Get details of a specific dataset by workspace slug and dataset slug."""
    data = _execute_graphql(
        user,
        "GetDatasetLink",
        {"workspaceSlug": workspace_slug, "datasetSlug": dataset_slug},
    )
    if "errors" in data:
        return data
    link = data.get("datasetLinkBySlug")
    if link is None:
        return {"error": "Dataset not found"}
    return link["dataset"]


MAX_READ_SIZE = 1024 * 1024


# TODO : those tools should be GraphQL mutations instead of REST endpoints, to be consistent with the rest of the API and to leverage GraphQL permissions, validation and audit (to be added).
#  For now we keep them as simple tools for internal use, but we should migrate them to GraphQL in the future.
def _get_workspace_with_perm(user, workspace_slug, perm):
    try:
        workspace = Workspace.objects.filter_for_user(user).get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        return None, {"error": "Workspace not found"}
    if not user.has_perm(perm, workspace):
        return None, {"error": "Permission denied"}
    return workspace, None


def _read_file_content(bucket_name: str, file_path: str) -> bytes:
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
def list_files(
    user, workspace_slug: str, prefix: str = "", page: int = 1, per_page: int = 30
) -> dict:
    """List files and directories in a workspace bucket. Use prefix to browse subdirectories (e.g. "data/")."""
    workspace, err = _get_workspace_with_perm(
        user, workspace_slug, "files.download_object"
    )
    if err:
        return err

    try:
        result = storage.list_bucket_objects(
            workspace.bucket_name, prefix=prefix or None, page=page, per_page=per_page
        )
    except Exception:
        return {"error": "Failed to list files"}

    return {
        "page_number": result.page_number,
        "has_next_page": result.has_next_page,
        "has_previous_page": result.has_previous_page,
        "items": [
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
        ],
    }


@tool
def read_file(user, workspace_slug: str, file_path: str) -> dict:
    """Read the content of a file from a workspace bucket. The file must be smaller than 1 MB and valid UTF-8 text."""
    workspace, err = _get_workspace_with_perm(
        user, workspace_slug, "files.download_object"
    )
    if err:
        return err

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
    workspace, err = _get_workspace_with_perm(
        user, workspace_slug, "files.create_object"
    )
    if err:
        return err

    encoded = content.encode("utf-8")
    storage.save_object(workspace.bucket_name, file_path, io.BytesIO(encoded))
    return {"success": True, "file_path": file_path, "size": len(encoded)}
