import os
import re

from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.utils.cache import patch_cache_control
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.files import storage
from hexa.files.utils import is_public_path, is_safe_path
from hexa.workspaces.models import Workspace

# How long a browser may reuse the redirect to a signed URL. Kept well under the
# shortest signature lifetime (10 minutes on the cloud backends) so a cached
# redirect never points at an expired URL.
PUBLIC_FILE_REDIRECT_MAX_AGE = 5 * 60

RANGE_HEADER_RE = re.compile(r"^bytes=(\d*)-(\d*)$")


class _RangeReader:
    """Reads at most `length` bytes from `file`, which is already at the start.

    Deliberately exposes neither `tell` nor `seek`: FileResponse would otherwise
    derive Content-Length from the whole file.
    """

    def __init__(self, file, length: int):
        self._file = file
        self._remaining = length

    def read(self, size: int = -1) -> bytes:
        if self._remaining <= 0:
            return b""
        if size < 0 or size > self._remaining:
            size = self._remaining
        chunk = self._file.read(size)
        self._remaining -= len(chunk)
        return chunk

    def close(self):
        self._file.close()


def _parse_range(header: str, size: int) -> tuple[int, int] | None:
    """The inclusive byte range a single-range header asks for, or None if unsatisfiable."""
    match = RANGE_HEADER_RE.match(header.strip())
    if match is None:
        return None
    first, last = match.groups()
    if first == "" and last == "":
        return None
    if first == "":
        suffix = int(last)
        if suffix == 0:
            return None
        return max(size - suffix, 0), size - 1
    start = int(first)
    end = min(int(last), size - 1) if last != "" else size - 1
    if start >= size or start > end:
        return None
    return start, end


def _file_response(request: HttpRequest, full_path: str, **kwargs) -> HttpResponse:
    """Serve a file, honouring a `Range` header with a 206 so that formats read in
    pieces (tile archives, large CSVs) work against the filesystem backend.
    """
    size = os.path.getsize(full_path)
    range_header = request.headers.get("Range")
    if range_header is None:
        response = FileResponse(open(full_path, "rb"), **kwargs)
        response["Accept-Ranges"] = "bytes"
        return response

    byte_range = _parse_range(range_header, size)
    if byte_range is None:
        response = HttpResponse(status=416)
        response["Content-Range"] = f"bytes */{size}"
        return response

    start, end = byte_range
    file = open(full_path, "rb")
    file.seek(start)
    response = FileResponse(_RangeReader(file, end - start + 1), status=206, **kwargs)
    response["Content-Length"] = str(end - start + 1)
    response["Content-Range"] = f"bytes {start}-{end}/{size}"
    response["Accept-Ranges"] = "bytes"
    return response


@xframe_options_exempt
def download_file(request: HttpRequest, token: str) -> HttpResponse:
    if hasattr(storage, "get_bucket_object_by_token") is False:
        return HttpResponseBadRequest("Storage does not support token-based access")
    try:
        object = storage.get_bucket_object_by_token(token)
    except storage.exceptions.BadRequest:
        return HttpResponseBadRequest("Invalid token")
    except storage.exceptions.NotFound:
        raise Http404("File not found")
    if object.type != "file":
        raise Http404("File not found")
    full_path = storage.path(object.path)
    as_attachment = request.GET.get("attachment", "false")
    return _file_response(
        request,
        full_path,
        as_attachment=as_attachment == "true",
        filename=object.name,
    )


@require_http_methods(["POST", "PUT"])
@csrf_exempt
def upload_file(request: HttpRequest, token: str) -> HttpResponse:
    if hasattr(storage, "save_object_by_token") is False:
        return HttpResponseBadRequest("Storage does not support token-based access")
    try:
        storage.save_object_by_token(token, request.body)
        return HttpResponse(status=201)
    except storage.exceptions.AlreadyExists:
        return HttpResponseBadRequest("Object already exists")
    except storage.exceptions.BadRequest:
        return HttpResponseBadRequest("Invalid token")


@require_http_methods(["GET", "HEAD"])
def public_file(request: HttpRequest, workspace_slug: str, path: str) -> HttpResponse:
    """Redirect anyone to a file of the workspace's public folder.

    The URL is stable while the signed URL it redirects to is not, so a web app
    keeps the former and never sees the latter expire. No login (``ANONYMOUS_URLS``
    in apps.py) and any origin (``allow_any_origin`` there too): the folder being
    public, on a workspace that opened it, is the whole authorization. Everything
    that is not such a file is a 404, so a visitor learns nothing about what else
    the bucket holds.
    """
    if not is_safe_path(path) or not is_public_path(path):
        raise Http404("File not found")
    try:
        workspace = Workspace.objects.get(
            slug=workspace_slug, public_files_enabled=True, archived=False
        )
    except Workspace.DoesNotExist:
        raise Http404("File not found")
    try:
        object = storage.get_bucket_object(workspace.bucket_name, path)
    except storage.exceptions.NotFound:
        raise Http404("File not found")
    if object.type != "file":
        raise Http404("File not found")

    download_url = storage.generate_download_url(
        bucket_name=workspace.bucket_name, target_key=path, force_attachment=False
    )
    response = HttpResponseRedirect(download_url)
    patch_cache_control(response, public=True, max_age=PUBLIC_FILE_REDIRECT_MAX_AGE)
    return response
