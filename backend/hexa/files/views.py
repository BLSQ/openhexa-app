import logging

from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.files import storage

logger = logging.getLogger(__name__)


@xframe_options_exempt
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
    logger.warning(f"upload_file called with token: {token[:20]}... body length: {len(request.body)}")
    if hasattr(storage, "save_object_by_token") is False:
        logger.warning("Storage does not support token-based access")
        return HttpResponseBadRequest("Storage does not support token-based access")
    try:
        logger.warning(f"Calling save_object_by_token...")
        storage.save_object_by_token(token, request.body)
        logger.warning("save_object_by_token completed successfully")
        return HttpResponse(status=201)
    except storage.exceptions.AlreadyExists:
        logger.warning("AlreadyExists exception")
        return HttpResponseBadRequest("Object already exists")
    except storage.exceptions.BadRequest as e:
        logger.warning(f"BadRequest exception: {e}")
        return HttpResponseBadRequest("Invalid token")
    except Exception as e:
        logger.exception(f"Unexpected exception: {e}")
        raise
