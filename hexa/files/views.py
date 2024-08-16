from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods

from hexa.files import storage


def download_file(request: HttpRequest, token: str) -> HttpResponse:
    print("download_file", "coucou", flush=True)
    object = storage.get_bucket_object_by_token(token)
    full_path = storage.path(object.path)
    return FileResponse(open(full_path, "rb"), as_attachment=True)


@require_http_methods(["POST", "PUT"])
def upload_file(request: HttpRequest, token: str) -> HttpResponse:
    file = request.FILES.get("file", None)
    if file is None:
        return HttpResponseBadRequest("Missing 'file' parameter")
    try:
        storage.save_object_by_token(token, file)
        return HttpResponse(status=201)
    except storage.exceptions.AlreadyExists:
        return HttpResponseBadRequest("Object already exists")
    except storage.exceptions.BadRequest:
        return HttpResponseBadRequest("Invalid token")
