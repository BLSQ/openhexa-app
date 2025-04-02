from hexa.app import CoreAppConfig


class FilesConfig(CoreAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.files"

    ANONYMOUS_URLS = [
        "files:upload_file",
        "files:download_file",
    ]
