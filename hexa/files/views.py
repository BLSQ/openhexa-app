import logging

from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.core.views_utils import disable_cors
from hexa.files import storage
from hexa.files.models import FileAccessRule
from hexa.workspaces.models import Workspace

logger = logging.getLogger(__name__)


def download_file(request: HttpRequest, token: str) -> HttpResponse:
    if hasattr(storage, "get_bucket_object_by_token") is False:
        return HttpResponseBadRequest("Storage does not support token-based access")
    object = storage.get_bucket_object_by_token(token)
    full_path = storage.path(object.path)
    as_attachment = request.GET.get("attachment", "false")
    return FileResponse(open(full_path, "rb"), as_attachment=as_attachment == "true")


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


@csrf_exempt
@disable_cors
def public_file_access(
    request: HttpRequest, workspace_slug: str, path: str
) -> HttpResponse:
    try:
        workspace = Workspace.objects.get(slug=workspace_slug)
        external_access = FileAccessRule.objects.is_active().find_nearest_access(
            workspace, path
        )

        if external_access is None:
            logger.debug(f"No external access match {workspace_slug}{path}")
            return HttpResponseNotFound()
        if external_access.auth_type != "public":
            raise NotImplementedError

        try:
            download_url = storage.generate_download_url(
                workspace.bucket_name, path.lstrip("/")
            )
            # In this first version, we just redirect to the download URL. Another approach
            # would be to stream the file directly from the storage backend.
            # (this has to be implemented for each storage backend)
            return HttpResponseRedirect(download_url)
        except storage.exceptions.NotFound:
            return HttpResponseNotFound()

    except (Workspace.DoesNotExist, FileAccessRule.DoesNotExist):
        logger.debug(f"Workspace {workspace_slug} or file {path} not found")
        return HttpResponseNotFound()
