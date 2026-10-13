from corsheaders.signals import check_request_enabled
from django.http import HttpRequest
from django.urls import Resolver404, resolve

from hexa.app import CoreAppConfig

# Views that any origin may call: the public folder is open to everyone by
# definition, and the filesystem backend's download view is where the public
# redirect lands on installs without a cloud bucket. Both carry their own
# authorization (the folder's visibility, a signed token), like a bucket's
# wildcard CORS rules.
ANY_ORIGIN_VIEWS = {"files:public_file", "files:download_file"}


def allow_any_origin(sender, request: HttpRequest, **kwargs) -> bool:
    if not request.path_info.startswith("/files/"):
        return False
    try:
        match = resolve(request.path_info)
    except Resolver404:
        return False
    return f"{match.app_name}:{match.url_name}" in ANY_ORIGIN_VIEWS


class FilesConfig(CoreAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.files"

    ANONYMOUS_URLS = [
        "files:upload_file",
        "files:download_file",
        "files:public_file",
    ]

    def ready(self):
        check_request_enabled.connect(allow_any_origin, dispatch_uid="files_any_origin")
