import io
import os
import shutil
from mimetypes import guess_type
from pathlib import Path

from django.core.files import locks
from django.core.signing import BadSignature, TimestampSigner
from django.urls import reverse
from django.utils._os import safe_join
from django.utils.text import get_valid_filename

from .base import ObjectsPage, Storage, StorageObject


class FileSystemStorage(Storage):
    def __init__(self, folder, prefix=""):
        self.location = Path(folder)
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
        return Path(safe_join(bucket_path, name))

    def size(self, name):
        return os.path.getsize(name)

    def to_storage_object(self, bucket_name: str, object_key: Path):
        full_path = self.bucket_path(bucket_name, object_key)
        if not self.exists(full_path):
            raise self.exceptions.NotFound(f"Object {object_key} not found")
        if full_path.is_file():
            return StorageObject(
                name=object_key.name,
                key=object_key,
                updated=os.path.getmtime(full_path),
                size=self.size(full_path),
                path=Path(bucket_name) / object_key,
                type="file",
                content_type=guess_type(full_path)[0] or "application/octet-stream",
            )
        else:
            return StorageObject(
                name=object_key.name,
                key=object_key,
                updated=os.path.getmtime(full_path),
                path=Path(bucket_name) / object_key,
                type="directory",
            )

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

    def get_bucket_object_by_token(self, token: str):
        try:
            signer = TimestampSigner()
            decoded_value = signer.unsign(token, max_age=60 * 60)
            return self.get_bucket_object(
                decoded_value["bucket_name"], decoded_value["target_key"]
            )
        except (UnicodeDecodeError, BadSignature):
            raise self.exceptions.BadRequest("Invalid token")

    def save_object_by_token(self, token: str, file: io.BufferedReader):
        try:
            signer = TimestampSigner()
            decoded_value = signer.unsign(token, max_age=60 * 60)
            self.save_object(
                decoded_value["bucket_name"], decoded_value["target_key"], file
            )
        except (UnicodeDecodeError, BadSignature):
            raise self.exceptions.BadRequest("Invalid token")

    def save_object(
        self, bucket_name: str, file_path: str, file: io.BufferedReader | bytes
    ):
        full_path = self.bucket_path(bucket_name, file_path)

        # Create any intermediate directories that do not exist.
        directory = os.path.dirname(full_path)
        try:
            os.makedirs(directory, exist_ok=True)
        except FileExistsError:
            raise FileExistsError(f"{directory} exists and is not a directory.")

        with open(full_path, "wb") as f:
            locks.lock(f, locks.LOCK_EX)
            if isinstance(file, bytes):
                f.write(file)
            else:
                f.write(file.read())
            locks.unlock(f)

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        folder_key = self.get_valid_filepath(folder_key)
        self.create_directory(f"{bucket_name}/{folder_key}")
        return folder_key

    def get_bucket_object(self, bucket_name: str, object_key: str):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        full_path = self.bucket_path(bucket_name, object_key)
        if not self.exists(full_path):
            raise self.exceptions.NotFound(f"Object {object_key} not found")
        return self.to_storage_object(bucket_name, object_key)

    def list_bucket_objects(
        self,
        bucket_name,
        prefix="",
        page: int = 1,
        per_page=30,
        query: str = None,
        ignore_hidden_files=True,
    ):
        full_path = self.bucket_path(bucket_name, prefix)
        if not os.path.exists(full_path):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        if not os.path.isdir(full_path):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} is not a directory")

        def does_object_match(name):
            if ignore_hidden_files and name.startswith("."):
                return False
            if query:
                return query.lower() in name.lower()
            return True

        objects = []
        root, dirs, files = next(os.walk(full_path))
        for dir in dirs:
            if does_object_match(dir) is False:
                continue
            dir_key = Path(prefix) / dir
            objects.append(self.to_storage_object(bucket_name, dir_key))
        for file in files:
            if does_object_match(file) is False:
                continue
            object_key = Path(prefix) / file
            objects.append(self.to_storage_object(bucket_name, object_key))

        offset = (page - 1) * per_page
        return ObjectsPage(
            items=objects[offset : offset + per_page],
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=len(objects) > page * per_page,
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
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        full_path = self.bucket_path(bucket_name, target_key)
        if self.exists(full_path) and raise_if_exists:
            raise self.exceptions.AlreadyExists(f"Object {target_key} already exist")

        signer = TimestampSigner()
        token = signer.sign_object(
            {"bucket_name": bucket_name, "target_key": target_key}
        )
        b64_token = signer.signature(token)
        return reverse("files:upload_file", args=(b64_token,))

    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False
    ):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        full_path = self.bucket_path(bucket_name, target_key)
        if not self.exists(full_path):
            raise self.exceptions.NotFound(f"Object {target_key} not found")

        signer = TimestampSigner()
        token = signer.sign_object(
            {"bucket_name": bucket_name, "target_key": target_key}
        )
        b64_token = signer.signature(token)
        return reverse("files:download_file", args=(b64_token,))

    def get_token_as_env_variables(self, token):
        return super().get_token_as_env_variables(token)
