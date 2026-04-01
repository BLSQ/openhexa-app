from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_files(
    user, workspace_slug: str, prefix: str = "", page: int = 1, per_page: int = 30
) -> dict:
    """List files and directories in a workspace bucket. Use prefix to browse subdirectories (e.g. 'data/'). Returns file name, path, type (file/directory), size, and last update. Use read_file with the file path to read text content."""
    data = execute_graphql(
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
    """Read the content of a text file from a workspace bucket. Only works for UTF-8 text files up to 1 MB (includes .py, .csv, .json, .ipynb, .sql, .txt, etc.). Use list_files first to check file size and path. For Jupyter notebooks (.ipynb), the content is JSON that you can parse to read/modify cells."""
    data = execute_graphql(
        user,
        "ReadFileContent",
        {"workspaceSlug": workspace_slug, "filePath": file_path},
    )
    if "errors" in data:
        return data
    return data["readFileContent"]


@tool
def write_file(user, workspace_slug: str, file_path: str, content: str) -> dict:
    """Write text content to a new file in a workspace bucket. Fails if the file already exists. Maximum 1 MB. For Jupyter notebooks, provide valid .ipynb JSON content. Requires createObject permission on the workspace."""
    data = execute_graphql(
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
