import json

from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_datasets(user, workspace_slug: str, page: int = 1, per_page: int = 10) -> dict:
    """List datasets in a workspace. Returns dataset summaries. Use get_dataset with the dataset slug to get full details including versions and files."""
    data = execute_graphql(
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
def get_dataset(
    user,
    workspace_slug: str,
    dataset_slug: str,
    versions_page: int = 1,
    versions_per_page: int = 10,
) -> dict:
    """Get full details of a dataset: metadata, permissions, all versions with their files, and the latest version's file list. Use a file 'id' from the response with preview_dataset_file to see sample data. Use the dataset 'id' with create_dataset_version to add a new version."""
    data = execute_graphql(
        user,
        "GetDataset",
        {
            "workspaceSlug": workspace_slug,
            "datasetSlug": dataset_slug,
            "versionsPage": versions_page,
            "versionsPerPage": versions_per_page,
        },
    )
    if "errors" in data:
        return data
    link = data.get("datasetLinkBySlug")
    if link is None:
        return {"error": "Dataset not found"}
    return link["dataset"]


@tool
def preview_dataset_file(user, file_id: str) -> dict:
    """Preview the content of a dataset file by its ID (from get_dataset's file list). Returns a sample of the data for tabular files (CSV, Parquet, etc.), file properties, and metadata. The sample status can be PROCESSING (still generating), FINISHED (sample ready), or FAILED."""
    data = execute_graphql(user, "PreviewDatasetFile", {"id": file_id})
    if "errors" in data:
        return data
    file_data = data.get("datasetVersionFile")
    if file_data is None:
        return {"error": "Dataset file not found"}
    return file_data


@tool
def create_dataset(user, workspace_slug: str, name: str, description: str = "") -> dict:
    """Create a new dataset in a workspace. Returns the created dataset with its ID and slug. After creating, use create_dataset_version to add a version, then upload files to the version."""
    data = execute_graphql(
        user,
        "CreateDataset",
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "name": name,
                "description": description or None,
            }
        },
    )
    if "errors" in data:
        return data
    return data["createDataset"]


@tool
def create_dataset_version(
    user, dataset_id: str, name: str, changelog: str = "", files_json: str = ""
) -> dict:
    r"""Create a new version of a dataset with optional inline files. Requires the dataset ID (from get_dataset or create_dataset) and a version name (e.g. 'v1', '2024-01'). Optionally provide a changelog describing what changed. To include files, provide files_json as a JSON array of {uri, contentType, content} objects, e.g. '[{"uri": "data.csv", "contentType": "text/csv", "content": "a,b\n1,2"}]'."""
    gql_input: dict = {
        "datasetId": dataset_id,
        "name": name,
        "changelog": changelog or None,
    }

    if files_json:
        try:
            files = json.loads(files_json)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in files_json"}
        if not isinstance(files, list) or not files:
            return {
                "error": "files_json must be a non-empty JSON array of {uri, contentType, content} objects"
            }
        gql_input["files"] = files

    data = execute_graphql(
        user,
        "CreateDatasetVersion",
        {"input": gql_input},
    )
    if "errors" in data:
        return data
    return data["createDatasetVersion"]
