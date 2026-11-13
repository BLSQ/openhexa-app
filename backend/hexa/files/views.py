from django.conf import settings
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.files import storage
from hexa.files.public import PUBLIC_FOLDER
from hexa.files.utils import is_safe_path
from hexa.workspaces.models import Workspace

PUBLIC_FILE_CACHE_MAX_AGE = 300


@xframe_options_exempt
def download_file(request: HttpRequest, token: str) -> HttpResponse:
    if hasattr(storage, "get_bucket_object_by_token") is False:
        return HttpResponseBadRequest("Storage does not support token-based access")
    object = storage.get_bucket_object_by_token(token)
    full_path = storage.path(object.path)
    as_attachment = request.GET.get("attachment", "false")
    response = FileResponse(
        open(full_path, "rb"), as_attachment=as_attachment == "true"
    )
    response["Content-Security-Policy"] = "sandbox"
    return response


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


def _with_public_cors(response: HttpResponse) -> HttpResponse:
    # Public files are meant to be embedded anywhere (web apps, maps, notebooks) and
    # carry no credentials, so any origin is allowed.
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Range"
    return response


@require_http_methods(["GET", "HEAD", "OPTIONS"])
def public_file(request: HttpRequest, workspace_slug: str, path: str) -> HttpResponse:
    if request.method == "OPTIONS":
        return _with_public_cors(HttpResponse(status=204))

    if not settings.PUBLIC_FILES_ENABLED:
        raise Http404
    workspace = Workspace.objects.filter(
        slug=workspace_slug, archived=False, public_files_enabled=True
    ).first()
    if workspace is None or not workspace.bucket_name:
        raise Http404
    if not path or not is_safe_path(path):
        raise Http404
    if any(part.startswith(".") for part in path.split("/")):
        raise Http404

    key = f"{PUBLIC_FOLDER}{path}"
    try:
        object = storage.get_bucket_object(workspace.bucket_name, key)
    except storage.exceptions.NotFound:
        raise Http404
    # Some backends resolve directory keys and sign URLs for any key, so only
    # existing files may be redirected to.
    if object.type != "file":
        raise Http404

    # Redirecting avoids streaming through Django and gives range requests for free.
    response = HttpResponseRedirect(
        storage.generate_download_url(
            bucket_name=workspace.bucket_name,
            # Not object.key: the filesystem backend returns it as a Path, which can't be signed
            target_key=key,
            # Never rendered as a page: on the filesystem backend the file is served from
            # the app origin, where an uploaded HTML or SVG file could run scripts with the
            # viewer's session. fetch(), <img> and range reads ignore this header.
            force_attachment=True,
        )
    )
    # Shorter than the lifetime of the shortest signed URL (10 minutes on GCS), so a cached
    # redirect never points to an expired URL, while repeated reads (map tiles) reuse it.
    response["Cache-Control"] = f"public, max-age={PUBLIC_FILE_CACHE_MAX_AGE}"
    response["Referrer-Policy"] = "no-referrer"
    return _with_public_cors(response)
