import time

from ariadne import QueryType
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from hexa.core.text_files import (
    AGENT_READ,
    GREP_HEAD_LIMIT,
    MAX_TEXT_FILE_SIZE,
    GrepOutputMode,
    TextFiles,
    read_window,
)
from hexa.files import storage
from hexa.files.backends.exceptions import NotFound
from hexa.files.bucket_file_source import MAX_LISTED_FILES, BucketFileSource
from hexa.files.utils import is_safe_path
from hexa.workspaces.models import Workspace

files_queries = QueryType()

# A windowed read (line range or numbered) may download a larger file than a full read,
# as long as what it returns stays under MAX_TEXT_FILE_SIZE.
MAX_WINDOWED_READ_SIZE = 10 * 1024 * 1024
# Every file grep searches is a full download; past these one call would hold a worker
# for minutes and outlast the proxy timeout.
GREP_MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
GREP_TIMEOUT_SECONDS = 20


@files_queries.field("getFileByPath")
def resolve_get_file_by_path(_, info, workspace_slug, path):
    request: HttpRequest = info.context["request"]

    if not is_safe_path(path):
        return None

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return None

    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")

    try:
        return storage.get_bucket_object(workspace.bucket_name, path)
    except NotFound:
        return None


@files_queries.field("readFileContent")
def resolve_read_file_content(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    workspace_slug = kwargs["workspace_slug"]
    file_path = kwargs["file_path"]

    if not is_safe_path(file_path):
        return {"success": False, "errors": ["INVALID_PATH"]}

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}

    if not request.user.has_perm("files.download_object", workspace):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    try:
        obj = storage.get_bucket_object(workspace.bucket_name, file_path)
    except NotFound:
        return {"success": False, "errors": ["NOT_FOUND"]}

    if obj.type != "file":
        return {"success": False, "errors": ["NOT_A_FILE"]}

    start_line = kwargs.get("start_line")
    end_line = kwargs.get("end_line")
    line_numbers = kwargs.get("line_numbers", False)
    windowed = line_numbers or start_line is not None or end_line is not None
    max_size = MAX_WINDOWED_READ_SIZE if windowed else MAX_TEXT_FILE_SIZE
    if obj.size > max_size:
        return {"success": False, "errors": ["FILE_TOO_LARGE"]}

    content = storage.read_object(workspace.bucket_name, file_path)
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return {"success": False, "errors": ["NOT_UTF8"]}

    if line_numbers:
        window = read_window(text, start_line, end_line, AGENT_READ)
    else:
        # Sliced with line endings kept, so a full read returns the file unchanged.
        lines = text.splitlines(keepends=True)
        start = max(start_line or 1, 1)
        end = min(end_line or len(lines), len(lines))
        window = {
            "content": "".join(lines[start - 1 : end]),
            "start_line": start,
            "end_line": end,
            "total_lines": len(lines),
        }
        if len(window["content"]) > MAX_TEXT_FILE_SIZE:
            return {"success": False, "errors": ["FILE_TOO_LARGE"]}
    return {"success": True, "errors": [], "size": len(content), **window}


def _bucket_files(request: HttpRequest, workspace_slug: str, prefix: str | None):
    """The workspace bucket's files under `prefix`, or the errors preventing access."""
    prefix = prefix or ""
    if prefix and not is_safe_path(prefix):
        return None, ["INVALID_PATH"]
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return None, ["NOT_FOUND"]
    if not request.user.has_perm("files.download_object", workspace):
        return None, ["PERMISSION_DENIED"]
    return BucketFileSource(storage, workspace.bucket_name, prefix), None


def _with_listing_notice(result: dict, source: BucketFileSource) -> dict:
    if source.truncated:
        notice = (
            f"Only the first {MAX_LISTED_FILES} files of the bucket were considered. "
            "Pass a prefix to narrow the search."
        )
        result["notice"] = " ".join(filter(None, [result.get("notice"), notice]))
    return {"success": True, "errors": [], **result}


@files_queries.field("globFiles")
def resolve_glob_files(_, info, workspace_slug, pattern, prefix=None):
    source, errors = _bucket_files(info.context["request"], workspace_slug, prefix)
    if errors:
        return {"success": False, "errors": errors}
    return _with_listing_notice(TextFiles(source).glob(pattern), source)


@files_queries.field("grepFiles")
def resolve_grep_files(
    _,
    info,
    workspace_slug,
    pattern,
    glob,
    prefix=None,
    output_mode=GrepOutputMode.FILES_WITH_MATCHES,
    ignore_case=False,
    context=0,
    head_limit=None,
    offset=0,
):
    source, errors = _bucket_files(info.context["request"], workspace_slug, prefix)
    if errors:
        return {"success": False, "errors": errors}
    # Started before the listing, which walks the bucket on the first access.
    deadline = time.monotonic() + GREP_TIMEOUT_SECONDS
    result = TextFiles(source).grep(
        pattern,
        glob=glob,
        output_mode=output_mode,
        ignore_case=ignore_case,
        context=context,
        head_limit=GREP_HEAD_LIMIT if head_limit is None else head_limit,
        offset=offset,
        should_stop=lambda: source.bytes_read >= GREP_MAX_DOWNLOAD_BYTES
        or time.monotonic() >= deadline,
    )
    if "error" in result:
        return {"success": False, "errors": ["INVALID_PATTERN"]}
    if "counts" in result:
        result["counts"] = [
            {"path": path, "count": count} for path, count in result["counts"].items()
        ]
    return _with_listing_notice(result, source)


bindables = [files_queries]
