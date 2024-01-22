from django.conf import settings

from .gcp import GCPClient
from .s3 import S3Client

default_mode = settings.WORKSPACE_STORAGE_ENGINE

mode = default_mode


def get_storage(mode=default_mode):
    if mode == "gcp":
        return GCPClient()
    if mode == "s3":
        return S3Client()
    raise Exception(f"unsupported filesystem {mode}")
