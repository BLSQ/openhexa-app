import io
import os
import shutil
from pathlib import Path

from django.utils._os import safe_join
from django.utils.text import get_valid_filename

from .base import Storage


class FileSystemStorage(Storage):
    def __init__(self, location, prefix=""):
        self.location = Path(location)
        self.prefix = prefix  # TODO: Use the prefix here to create the bucket path and not in workspace model

    def exists(self, name):
        try:
            exists = os.path.lexists(self.path(name))
            return exists
        except self.exceptions.SuspiciousFileOperation:
            raise

    def path(self, name):
        return safe_join(self.location, name)

    def bucket_path(self, bucket_name, name):
        bucket_path = self.path(bucket_name)
        return safe_join(bucket_path, name)

    def size(self, name):
        return os.path.getsize(self.path(name))

    def get_valid_filepath(self, path: str | Path):
        """Returns a path where all the directories and the filename are valid.

        Args:
            path (str|Path): A path
        """
        return "/".join(get_valid_filename(part) for part in path.split("/"))

    def create_directory(self, name):
        assert (
            self.get_valid_filepath(name) == name
        ), f"Invalid directory name: {name}. Please use a valid name."

        if self.exists(name):
            raise self.exceptions.AlreadyExists(f"Directory {name} already exists")
        os.makedirs(self.path(name), exist_ok=True)

    def create_bucket(self, bucket_name: str, *args, **kwargs):
        if "/" in bucket_name:
            raise self.exceptions.SuspiciousFileOperation(
                "Bucket name cannot contain '/'"
            )
        valid_bucket_name = get_valid_filename(bucket_name)
        self.create_directory(valid_bucket_name)
        return valid_bucket_name

    def delete_bucket(self, bucket_name: str, fully: bool = False):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        return shutil.rmtree(self.path(bucket_name))

    def save_object(
        self, bucket_name: str, file_path: str, file: io.BufferedReader | bytes
    ):
        full_path = self.bucket_path(bucket_name, file_path)
        with open(full_path, "wb") as f:
            if isinstance(file, bytes):
                f.write(file)
            else:
                f.write(file.read())

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        folder_key = self.get_valid_filepath(folder_key)
        self.create_directory(f"{bucket_name}/{folder_key}")
        return folder_key

    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False
    ):
        return super().generate_download_url(bucket_name, target_key, force_attachment)

    def get_bucket_object(self, bucket_name: str, object_key: str):
        pass

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
