from pathlib import Path

from django.http import HttpRequest
from graphql import graphql_sync

from config.schema import schema

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


@tool
def list_files(
    user, workspace_slug: str, prefix: str = "", page: int = 1, per_page: int = 30
) -> dict:
    """List files and directories in a workspace bucket. Use prefix to browse subdirectories (e.g. "data/")."""
    data = _execute_graphql(
        user,
        "ListFiles",
        {
            "workspaceSlug": workspace_slug,
            "prefix": prefix or None,
            "page": page,
            "perPage": per_page,
        },
    )
    if "errors" in data:
        return data
    workspace = data.get("workspace")
    if workspace is None:
        return {"error": "Workspace not found"}
    return workspace["bucket"]["objects"]


@tool
def read_file(user, workspace_slug: str, file_path: str) -> dict:
    """Read the content of a file from a workspace bucket."""
    data = _execute_graphql(
        user,
        "ReadFileContent",
        {"workspaceSlug": workspace_slug, "filePath": file_path},
    )
    if "errors" in data:
        return data
    return data["readFileContent"]


@tool
def write_file(user, workspace_slug: str, file_path: str, content: str) -> dict:
    """Write text content to a new file in a workspace bucket. Fails if the file already exists."""
    data = _execute_graphql(
        user,
        "WriteFileContent",
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "filePath": file_path,
                "content": content,
                "overwrite": False,
            }
        },
    )
    if "errors" in data:
        return data
    return data["writeFileContent"]
