import hashlib
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
    """Get full details of a dataset: metadata, its versions (name, changelog, date) and the file list of the latest version only. Use a file 'id' from the response with preview_dataset_file to see its columns. Use the dataset 'id' with create_dataset_version to add a new version."""
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


def _column_types(attributes: list[dict]) -> dict[str, str]:
    """Map md5(column name) to the data type recorded by the dataset profiling."""
    types = {}
    for attribute in attributes:
        column_hash, _, key = attribute["key"].rpartition(".")
        if attribute["system"] and key == "data_type":
            types[column_hash] = attribute["value"]
    return types


@tool
def preview_dataset_file(user, file_id: str) -> dict:
    """Describe a dataset file by its ID (from get_dataset's file list). Returns file metadata and, for tabular files (CSV, Parquet, etc.), 'rows' (the row count of the whole file) and the ordered 'columns' as {name, type} objects. File content and sample rows are never returned, as they may hold sensitive data. 'columns' is null when the file has not been profiled, and 'profiling' ({status}) tells why: it is null for non-tabular files, PROCESSING while the file is still being read (try again later), FAILED when the file could not be profiled (permanent) and FINISHED with null 'columns' when the columns could not be determined (permanent). A column 'type' is null when profiling could not determine it."""
    data = execute_graphql(user, "PreviewDatasetFile", {"id": file_id})
    if "errors" in data:
        return data
    file_data = data.get("datasetVersionFile")
    if file_data is None:
        return {"error": "Dataset file not found"}

    file_data["profiling"] = file_data.pop("fileSample")
    # Only the data type is taken from the profiling attributes: the other statistics
    # (minimum, maximum, ...) are values taken from the data itself.
    types = _column_types(file_data.pop("attributes"))
    if file_data["columns"] is not None:
        file_data["columns"] = [
            # Profiling attributes are keyed by the md5 hash of the column name.
            {"name": name, "type": types.get(hashlib.md5(name.encode()).hexdigest())}
            for name in file_data["columns"]
        ]
    return file_data


@tool(write=True)
def create_dataset(
    user,
    workspace_slug: str,
    name: str,
    files_json: str,
    description: str = "",
) -> dict:
    r"""Create a new dataset in a workspace with an initial version (v1) containing the provided files. The files_json parameter is a JSON array of {uri, contentType, content} objects, e.g. '[{"uri": "data.csv", "contentType": "text/csv", "content": "a,b\n1,2"}]'. Use create_dataset_version to add more versions later."""
    try:
        files = json.loads(files_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in files_json"}
    if not isinstance(files, list) or not files:
        return {
            "error": "files_json must be a non-empty JSON array of {uri, contentType, content} objects"
        }

    data = execute_graphql(
        user,
        "CreateDataset",
        {
            "input": {
                "workspaceSlug": workspace_slug,
                "name": name,
                "description": description or None,
                "files": files,
            }
        },
    )
    if "errors" in data:
        return data
    return data["createDataset"]


@tool(write=True)
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
