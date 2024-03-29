from django.conf import settings

from .basefs import NotFound
from .gcp import GCPClient
from .s3 import S3Client


def get_storage(mode=settings.WORKSPACE_STORAGE_ENGINE):
    if mode == "gcp":
        return GCPClient()
    if mode == "s3":
        return S3Client()
    raise Exception(f"unsupported filesystem {mode}")


NotFound = NotFound
