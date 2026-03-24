import base64
import io
from pathlib import Path
from zipfile import ZipFile

from django.http import HttpRequest
from graphql import graphql_sync

from config.schema import schema
from hexa.mcp.protocol import tool
from hexa.pipelines.models import PipelineFunctionalType

_QUERIES_PATH = Path(__file__).parent / "graphql" / "queries.graphql"
_QUERIES_SOURCE = _QUERIES_PATH.read_text()


def _execute_graphql(user, operation_name: str, variables=None):
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
        return {"errors": ["Workspace not found"]}
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
        return {"errors": ["Dataset not found"]}
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
        return {"errors": ["Workspace not found"]}
    return workspace["bucket"]["objects"]


@tool
def read_file(user, workspace_slug: str, file_path: str) -> dict:
    """Read the content of a file from a workspace bucket. Only works for UTF-8 text files up to 1 MB. Check the file size from list_files before calling."""
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
    """Write text content to a new file in a workspace bucket. Fails if the file already exists. Maximum file size is 1 MB. Requires the createObject permission on the workspace."""
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


@tool
def create_pipeline_version(
    user,
    workspace_slug: str,
    pipeline_code: str,
    source_code: str,
    version_name: str = "",
    description: str = "",
) -> dict:
    """Create a new version for an existing pipeline by uploading Python source code.

    The source_code is packaged into a zip archive as pipeline.py and uploaded as a new
    PipelineVersion. Pipeline parameters are extracted automatically from the source code.
    Only call this after create_pipeline has returned success=true.
    """
    buf = io.BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr("pipeline.py", source_code)
    zipfile_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    data = _execute_graphql(
        user,
        "UploadPipeline",
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "code": pipeline_code,
                "zipfile": zipfile_b64,
                "name": version_name,
                "description": description or None,
            }
        },
    )
    if "errors" in data:
        return data
    return data.get("uploadPipeline", {})


@tool
def create_pipeline(
    user,
    workspace_slug: str,
    name: str,
    description: str = "",
    functional_type: PipelineFunctionalType | None = None,
) -> dict:
    """Create a new pipeline in a workspace. Returns the created pipeline's id, code, and name."""
    data = _execute_graphql(
        user,
        "CreatePipeline",
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "name": name,
                "description": description or None,
                "functionalType": functional_type or None,
            }
        },
    )
    if "errors" in data:
        return data
    return data.get("createPipeline", {})
