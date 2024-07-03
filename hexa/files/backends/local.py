import os
from pathlib import Path

from django.conf import settings
from django.utils._os import safe_join

from .base import BaseClient


class FilesSystemStorage(BaseClient):
    @property
    def location(self):
        if not settings.WORKSPACE_STORAGE_BACKEND_LOCAL_FOLDER:
            raise ValueError("WORKSPACE_STORAGE_BACKEND_LOCAL_FOLDER is not set")
        return Path(settings.WORKSPACE_STORAGE_BACKEND_LOCAL_FOLDER)

    def path(self, name):
        return safe_join(self.location, name)

    def size(self, name):
        return os.path.getsize(self.path(name))

    def create_bucket(self, bucket_name: str, *args, **kwargs):
        return super().create_bucket(bucket_name, *args, **kwargs)

    def delete_bucket(self, bucket_name: str, fully: bool = False):
        return super().delete_bucket(bucket_name, fully)

    def upload_object(self, bucket_name: str, file_name: str, source: str):
        return super().upload_object(bucket_name, file_name, source)

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        pass

    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False
    ):
        return super().generate_download_url(bucket_name, target_key, force_attachment)

    def get_bucket_object(self, bucket_name: str, object_key: str):
        return super().get_bucket_object(bucket_name, object_key)

    def list_bucket_objects(
        self,
        bucket_name,
        prefix=None,
        page: int = 1,
        per_page=30,
        query=None,
        ignore_hidden_files=True,
    ):
        return super().list_bucket_objects(
            bucket_name, prefix, page, per_page, query, ignore_hidden_files
        )

    def get_short_lived_downscoped_access_token(self, bucket_name):
        return super().get_short_lived_downscoped_access_token(bucket_name)

    def generate_upload_url(
        self,
        bucket_name: str,
        target_key: str,
        content_type: str,
        raise_if_exists=False,
    ):
        return super().generate_upload_url(
            bucket_name, target_key, content_type, raise_if_exists
        )

    def get_token_as_env_variables(self, token):
        return super().get_token_as_env_variables(token)
