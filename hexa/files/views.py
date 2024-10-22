from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.files import storage


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
    if hasattr(storage, "save_object_by_token") is False:
        return HttpResponseBadRequest("Storage does not support token-based access")
    try:
        storage.save_object_by_token(token, request.body)
        return HttpResponse(status=201)
    except storage.exceptions.AlreadyExists:
        return HttpResponseBadRequest("Object already exists")
    except storage.exceptions.BadRequest:
        return HttpResponseBadRequest("Invalid token")
