import base64
import io
from pathlib import Path
from zipfile import ZipFile

from django.http import HttpRequest
from graphql import graphql_sync

from hexa.mcp.protocol import tool
from hexa.pipelines.models import Pipeline, PipelineFunctionalType

_QUERIES_PATH = Path(__file__).parent / "graphql" / "queries.graphql"
_QUERIES_SOURCE = _QUERIES_PATH.read_text()


def _execute_graphql(user, operation_name: str, variables=None):
    # Lazy import to avoid possible circular dependencies
    from config.schema import schema
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
def create_pipeline(
    user,
    workspace_slug: str,
    name: str,
    description: str = "",
    functional_type: PipelineFunctionalType | None = None,
    source_code: str | None = None,
) -> dict:
    """Create a new pipeline in the current workspace. Optionally upload Python source code as the first version (v1).

    Always provide a meaningful description summarizing what the pipeline does.
    If the pipeline has no clear purpose or is blank, use "" as the description.
    Only name, description, and functional_type are supported at creation time.
    Fields such as schedule, timeout, tags, or webhook settings cannot be set here.

    If source_code is omitted, the pipeline is created without any version.

    The source_code must follow this structure:

        from openhexa.sdk import current_run, pipeline


        @pipeline("Simple ETL")
        def simple_etl():
            count = task_1()
            task_2(count)


        @simple_etl.task
        def task_1():
            current_run.log_info("In task 1...")
            return 42


        @simple_etl.task
        def task_2(count):
            current_run.log_info(f"In task 2... count is {count}")


        if __name__ == "__main__":
            simple_etl()
    """
    create_data = _execute_graphql(
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
    if "errors" in create_data:
        return create_data
    pipeline_result = create_data.get("createPipeline", {})
    if not pipeline_result.get("success"):
        return pipeline_result

    pipeline = pipeline_result["pipeline"]

    if not source_code:
        return {"success": True, "pipeline": pipeline}

    pipeline_id = pipeline["id"]
    pipeline_code = pipeline["code"]

    buf = io.BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr("pipeline.py", source_code)
    zipfile_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    version_data = _execute_graphql(
        user,
        "UploadPipeline",
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "code": pipeline_code,
                "zipfile": zipfile_b64,
                "name": "",
                "description": None,
            }
        },
    )

    if "errors" in version_data or not version_data.get("uploadPipeline", {}).get(
        "success"
    ):
        Pipeline.objects.filter(id=pipeline_id).delete()
        return version_data.get("uploadPipeline", version_data)

    return {
        "success": True,
        "pipeline": pipeline,
        "pipelineVersion": version_data["uploadPipeline"]["pipelineVersion"],
    }
