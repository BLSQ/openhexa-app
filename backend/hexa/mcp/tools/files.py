from hexa.core.text_files import GREP_HEAD_LIMIT, GrepOutputMode
from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_files(
    user, workspace_slug: str, prefix: str = "", page: int = 1, per_page: int = 30
) -> dict:
    """List files and directories in a workspace bucket. Use prefix to browse subdirectories (e.g. 'data/'). Returns file name, key (the path to pass to the other file tools), type (file/directory), size, and last update. Use read_file with the key to read text content."""
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
def glob_files(user, workspace_slug: str, pattern: str, prefix: str = "") -> dict:
    """Find files in a workspace bucket by path pattern, at any depth, e.g. `**/*.csv`, `data/**/*.py` or `*.{json,yaml}`. `*` stays within a directory and `**` spans any depth. Pass prefix (e.g. 'data/') to search one directory only, which is much faster on large buckets. Returns sorted paths, at most 100: when `truncated` is true, narrow the pattern. Hidden files are skipped."""
    data = execute_graphql(
        user,
        "GlobFiles",
        {"workspaceSlug": workspace_slug, "pattern": pattern, "prefix": prefix},
    )
    if "errors" in data:
        return data
    return data["globFiles"]


@tool
def grep_files(
    user,
    workspace_slug: str,
    pattern: str,
    glob: str,
    prefix: str = "",
    output_mode: GrepOutputMode = GrepOutputMode.FILES_WITH_MATCHES,
    ignore_case: bool = False,
    context: int = 0,
    head_limit: int = GREP_HEAD_LIMIT,
    offset: int = 0,
) -> dict:
    """Search the contents of text files in a workspace bucket with a Python regular expression.

    EXPENSIVE: every file searched is downloaded in full. Keep `glob` (required, e.g. `scripts/**/*.py`) and `prefix` as narrow as possible, and prefer list_files or glob_files when the file name is enough. Text files over 1 MB are skipped.

    Patterns match within a single line; escape regex metacharacters. output_mode: `files_with_matches` (default) lists matching paths, which stops downloading once a page is full; `content` returns matching lines as `path:line:text`, with `context` lines around each match; `count` returns matches per file and their total, and downloads every file matching `glob`. head_limit and offset page through the entries; `truncated` tells there are more.

    A search stops after downloading 50 MB or running 20 seconds, and returns what it found so far with a notice.
    """
    data = execute_graphql(
        user,
        "GrepFiles",
        {
            "workspaceSlug": workspace_slug,
            "pattern": pattern,
            "glob": glob,
            "prefix": prefix,
            "outputMode": GrepOutputMode(output_mode).name,
            "ignoreCase": ignore_case,
            "context": context,
            "headLimit": head_limit,
            "offset": offset,
        },
    )
    if "errors" in data:
        return data
    result = data["grepFiles"]
    if result["counts"] is not None:
        result["counts"] = {c["path"]: c["count"] for c in result["counts"]}
    return result


@tool
def read_file(
    user,
    workspace_slug: str,
    file_path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    line_numbers: bool = False,
) -> dict:
    """Read the content of a text file from a workspace bucket. Only works for UTF-8 text files (includes .py, .csv, .json, .ipynb, .sql, .txt, etc.) up to 1 MB, or 10 MB when reading a line range or with line_numbers. Use list_files first to check file size and path. For Jupyter notebooks (.ipynb), the content is JSON that you can parse to read/modify cells. Use start_line and end_line (1-indexed, inclusive) to read a specific range of lines instead of the entire file. Returns `startLine`, `endLine` and `totalLines`, so you can tell whether there is more to read.

    Pass line_numbers=true to read source code: each line is prefixed with its number (`     N<TAB>line`, not part of the file), a read returns at most 2000 lines with a notice telling how to read the rest, and lines over 2000 characters are clipped.
    """
    data = execute_graphql(
        user,
        "ReadFileContent",
        {
            "workspaceSlug": workspace_slug,
            "filePath": file_path,
            "startLine": start_line,
            "endLine": end_line,
            "lineNumbers": line_numbers,
        },
    )
    if "errors" in data:
        return data
    return data["readFileContent"]


@tool(write=True)
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
