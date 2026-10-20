from hexa.core.text_files import (
    AGENT_READ,
    GREP_HEAD_LIMIT,
    GrepOutputMode,
    TextFiles,
)
from hexa.files import storage
from hexa.files.bucket_file_source import MAX_LISTED_FILES, BucketFileSource
from hexa.files.utils import is_safe_path
from hexa.mcp.protocol import tool
from hexa.workspaces.models import Workspace

from ._graphql import execute_graphql


def _bucket_files(user, workspace_slug: str, prefix: str):
    """The bucket's files under `prefix`, or an error, with readFileContent's checks."""
    if prefix and not is_safe_path(prefix):
        return None, {"error": "Invalid prefix"}
    workspace = (
        Workspace.objects.filter_for_user(user).filter(slug=workspace_slug).first()
    )
    if workspace is None:
        return None, {"error": "Workspace not found"}
    if not user.has_perm("files.download_object", workspace):
        return None, {"error": "Permission denied"}
    return BucketFileSource(storage, workspace.bucket_name, prefix), None


def _with_listing_notice(result: dict, source: BucketFileSource) -> dict:
    if source.truncated:
        result["notice"] = (
            f"Only the first {MAX_LISTED_FILES} files of the bucket were considered. "
            "Pass a prefix to narrow the search."
        )
    return result


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
def glob_files(user, workspace_slug: str, pattern: str, prefix: str = "") -> dict:
    """Find files in a workspace bucket by path pattern, at any depth, e.g. `**/*.csv`, `data/**/*.py` or `*.{json,yaml}`. `*` stays within a directory and `**` spans any depth. Pass prefix (e.g. 'data/') to search one directory only, which is much faster on large buckets. Returns sorted paths, at most 100: when `truncated` is true, narrow the pattern. Hidden files are skipped."""
    source, error = _bucket_files(user, workspace_slug, prefix)
    if error:
        return error
    return _with_listing_notice(TextFiles(source).glob(pattern), source)


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
    """
    source, error = _bucket_files(user, workspace_slug, prefix)
    if error:
        return error
    result = TextFiles(source).grep(
        pattern,
        glob=glob,
        output_mode=output_mode,
        ignore_case=ignore_case,
        context=context,
        head_limit=head_limit,
        offset=offset,
    )
    return _with_listing_notice(result, source)


@tool
def read_file(
    user,
    workspace_slug: str,
    file_path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    line_numbers: bool = False,
) -> dict:
    """Read the content of a text file from a workspace bucket. Only works for UTF-8 text files up to 1 MB (includes .py, .csv, .json, .ipynb, .sql, .txt, etc.). Use list_files first to check file size and path. For Jupyter notebooks (.ipynb), the content is JSON that you can parse to read/modify cells. Use start_line and end_line (1-indexed, inclusive) to read a specific range of lines instead of the entire file.

    Pass line_numbers=true to read source code: each line is prefixed with its number (`     N<TAB>line`, not part of the file), a read returns at most 2000 lines with a notice telling how to read the rest, lines over 2000 characters are clipped, and `total_lines` is returned.
    """
    variables = {"workspaceSlug": workspace_slug, "filePath": file_path}
    # Numbering needs the whole file, so the window is cut here rather than by the API.
    if start_line is not None and not line_numbers:
        variables["startLine"] = start_line
    if end_line is not None and not line_numbers:
        variables["endLine"] = end_line
    data = execute_graphql(
        user,
        "ReadFileContent",
        variables,
    )
    if "errors" in data:
        return data
    result = data["readFileContent"]
    if not line_numbers or not result.get("success"):
        return result
    return {
        **result,
        **TextFiles({file_path: result["content"]}).read(
            file_path, start_line, end_line, AGENT_READ
        ),
    }


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
