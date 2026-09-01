import json

from hexa.mcp.protocol import tool

from ._graphql import execute_graphql

# LLM callers only need enough rows to infer the schema and value shapes; the stored
# sample (WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE rows) is sized for the UI table.
PREVIEW_SAMPLE_ROWS = 3


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


def _sample_rows(file_data: dict) -> list:
    file_sample = file_data.get("fileSample")
    if not file_sample:
        return []
    return file_sample.get("sample") or []


def _column_names(file_data: dict) -> list:
    """Turn the stored profiling properties into a plain ordered list of column names.

    `properties` maps md5 hashes to column names for the web UI; the hashes are
    meaningless to a model, so only the names in file order are kept.
    """
    properties = file_data.pop("properties", None) or {}
    columns = properties.get("columns") or {}
    column_order = properties.get("column_order") or []
    names = [columns[key] for key in column_order if key in columns]
    return names or list(columns.values())


def _ordered_row(row: dict, columns: list) -> dict:
    """Restore the file's column order, which jsonb does not preserve in the sample.

    Columns the profiling could not handle are missing from `columns`; they are kept
    at the end so the sample never loses data.
    """
    ordered = {name: row[name] for name in columns if name in row}
    ordered.update({key: value for key, value in row.items() if key not in ordered})
    return ordered


@tool
def preview_dataset_file(user, file_id: str) -> dict:
    """Preview the content of a dataset file by its ID (from get_dataset's file list). Returns file metadata and, for tabular files (CSV, Parquet, etc.), the first few rows of the stored sample, with the columns of each row in the order they appear in the file. When no sample row is available, the ordered 'columns' of the file are returned instead. This is a preview only: 'rows' is the row count of the whole file and 'fileSample.sampleRowsAvailable' the size of the stored sample, both usually larger than the number of rows returned here. The sample status can be PROCESSING (still generating), FINISHED (sample ready), or FAILED."""
    data = execute_graphql(user, "PreviewDatasetFile", {"id": file_id})
    if "errors" in data:
        return data
    file_data = data.get("datasetVersionFile")
    if file_data is None:
        return {"error": "Dataset file not found"}

    columns = _column_names(file_data)
    rows = _sample_rows(file_data)
    file_sample = file_data.get("fileSample")
    if file_sample:
        file_sample["sample"] = [
            _ordered_row(row, columns) for row in rows[:PREVIEW_SAMPLE_ROWS]
        ]
        file_sample["sampleRowsAvailable"] = len(rows)
    # The sample rows already name every column, so `columns` would only repeat them.
    if not rows and columns:
        file_data["columns"] = columns
    return file_data


@tool
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
