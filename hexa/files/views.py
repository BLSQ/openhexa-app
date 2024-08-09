from django.http import FileResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods

from hexa.files import storage


def download_file(request: HttpRequest, token: str) -> HttpResponse:
    object = storage.get_bucket_object_by_token(token, "")
    full_path = storage.path(object.path)
    return FileResponse(open(full_path, "rb"), as_attachment=True)


@require_http_methods(["PUT"])
def upload_file(request: HttpRequest, token: str) -> HttpResponse:
    # file = request.FILES["file"]
    # object = storage.save_object_by_token(token, file)
    return HttpResponse(status=201)
