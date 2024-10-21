import io
import os
import shutil
from datetime import datetime
from mimetypes import guess_type
from pathlib import Path

from django.conf import settings
from django.core.files import locks
from django.core.signing import BadSignature, TimestampSigner
from django.urls import reverse
from django.utils._os import safe_join as django_safe_join
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.text import get_valid_filename

from .base import ObjectsPage, Storage, StorageObject, load_bucket_sample_data_with


def safe_join(base, *paths):
    """
    A version of django.utils._os.safe_join that returns a Path object.
    """
    return Path(django_safe_join(base, *paths))


class FileSystemStorage(Storage):
    storage_type = "local"

    def __init__(
        self,
        data_dir: str,
        ext_bind_path: str = None,
        file_permissions_mode: int | None = None,
        directory_permissions_mode: int | None = None,
    ):
        """Initialises the FileSystemStorage backend.

        Args:
            data_dir (str): Directory where the data will be stored.
            ext_bing_path (str, optional): When running in a docker container, it represents the path to the data_dir from context of the docker engine. Defaults to None.
            file_permissions_mode (int, optional): File permissions mode. Defaults to None.
            directory_permissions_mode (int, optional): Directory permissions mode. Defaults to None.
        """
        self.data_dir = Path(data_dir)
        self.ext_bind_path = Path(ext_bind_path) if ext_bind_path is not None else None
        self.file_permissions_mode = file_permissions_mode
        self.directory_permissions_mode = directory_permissions_mode
        self._token_max_age = 60 * 60  # 1 hour

    def _ensure_location_group_id(self, full_path):
        if os.name == "posix":
            file_gid = os.stat(full_path).st_gid
            data_dir_gid = os.stat(self.data_dir).st_gid
            if file_gid != data_dir_gid:
                try:
                    os.chown(full_path, uid=-1, gid=data_dir_gid)
                except PermissionError:
                    pass

    def load_bucket_sample_data(self, bucket_name: str):
        load_bucket_sample_data_with(bucket_name, self)

    def bucket_exists(self, bucket_name: str):
        return self.exists(bucket_name)

    def is_directory_empty(self, bucket_name: str, *paths):
        return not bool(next(os.scandir(self.path(bucket_name, *paths)), None))

    def exists(self, name):
        try:
            exists = os.path.lexists(self.path(name))
            return exists
        except self.exceptions.SuspiciousFileOperation:
            raise

    def path(self, *paths):
        return safe_join(self.data_dir, *paths)

    def size(self, name):
        return os.path.getsize(name)

    def _get_payload_from_token(self, token):
        try:
            signer = TimestampSigner()
            decoded_token = force_str(urlsafe_base64_decode(token))
            payload = signer.unsign_object(decoded_token, max_age=self._token_max_age)
            return payload
        except (UnicodeDecodeError, BadSignature, ValueError):
            raise self.exceptions.BadRequest("Invalid token")

    def _create_token_for_payload(self, payload: dict):
        signer = TimestampSigner()
        signed_payload = signer.sign_object(payload, compress=True)
        return urlsafe_base64_encode(force_bytes(signed_payload))

    def to_storage_object(self, bucket_name: str, object_key: Path):
        full_path = self.path(bucket_name, object_key)
        if not self.exists(full_path):
            raise self.exceptions.NotFound(f"Object {object_key} not found")
        if full_path.is_file():
            return StorageObject(
                name=object_key.name,
                key=object_key,
                updated=datetime.fromtimestamp(
                    os.path.getmtime(str(full_path))
                ).isoformat(),
                size=self.size(full_path),
                path=Path(bucket_name) / object_key,
                type="file",
                content_type=guess_type(full_path)[0] or "application/octet-stream",
            )
        else:
            return StorageObject(
                name=object_key.name,
                key=object_key,
                updated=datetime.fromtimestamp(os.path.getmtime(str(full_path))),
                path=Path(bucket_name) / object_key,
                type="directory",
            )

    def get_valid_filepath(self, path: str | Path):
        """Returns a path where all the directories and the filename are valid.

        Args:
            path (str|Path): A path
        """
        return "/".join(get_valid_filename(part) for part in str(path).split("/"))

    def create_directory(self, directory_path: str):
        if self.exists(directory_path):
            raise self.exceptions.AlreadyExists("Directory already exists")
        directory = self.path(directory_path)

        try:
            if self.directory_permissions_mode is not None:
                # Set the umask because os.makedirs() doesn't apply the "mode"
                # argument to intermediate-level directories.
                old_umask = os.umask(0o777 & ~self.directory_permissions_mode)
                try:
                    os.makedirs(
                        directory, self.directory_permissions_mode, exist_ok=True
                    )
                finally:
                    os.umask(old_umask)
            else:
                os.makedirs(directory, exist_ok=True)
        except FileExistsError:
            raise FileExistsError("%s exists and is not a directory." % directory)

    def create_bucket(self, bucket_name: str, *args, **kwargs):
        if "/" in bucket_name:
            raise self.exceptions.SuspiciousFileOperation(
                "Bucket name cannot contain '/'"
            )
        valid_bucket_name = get_valid_filename(bucket_name)
        self.create_directory(valid_bucket_name)
        return valid_bucket_name

    def delete_bucket(self, bucket_name: str, force: bool = False):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        if not force and not self.is_directory_empty(bucket_name):
            raise self.exceptions.BadRequest("Bucket is not empty")
        return shutil.rmtree(self.path(bucket_name))

    def get_bucket_object_by_token(self, token: str):
        payload = self._get_payload_from_token(token)
        return self.get_bucket_object(payload["bucket_name"], payload["file_path"])

    def save_object_by_token(self, token: str, file: io.BufferedReader):
        payload = self._get_payload_from_token(token)
        return self.save_object(payload["bucket_name"], payload["file_path"], file)

    def save_object(
        self, bucket_name: str, file_path: str, file: io.BufferedReader | bytes
    ):
        full_path = self.path(bucket_name, file_path)

        # Create any intermediate directories that do not exist.
        if not self.exists(full_path.parent):
            self.create_directory(full_path.parent)

        f = open(full_path, "wb")
        locks.lock(f, locks.LOCK_EX)
        try:
            if isinstance(file, bytes):
                f.write(file)
            else:
                f.write(file.read())
        finally:
            locks.unlock(f)
            f.close()

        if self.file_permissions_mode is not None:
            os.chmod(full_path, self.file_permissions_mode)

        # Ensure the moved file has the same gid as the storage root.
        self._ensure_location_group_id(full_path)

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        folder_key = self.get_valid_filepath(folder_key)
        self.create_directory(f"{bucket_name}/{folder_key}")
        return self.get_bucket_object(bucket_name, folder_key)

    def get_bucket_object(self, bucket_name: str, object_key: str):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        full_path = self.path(bucket_name, object_key)
        if not self.exists(full_path):
            raise self.exceptions.NotFound(f"Object {object_key} not found")
        return self.to_storage_object(bucket_name, Path(object_key))

    def list_bucket_objects(
        self,
        bucket_name,
        prefix="",
        page: int = 1,
        per_page=30,
        query: str = None,
        ignore_hidden_files=True,
    ):
        if prefix is None:
            prefix = ""
        full_path = self.path(bucket_name, prefix)
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

    def delete_object(self, bucket_name: str, object_key: str):
        full_path = self.path(bucket_name, object_key)
        if not self.exists(full_path):
            raise self.exceptions.NotFound(f"Object {object_key} not found")
        obj = self.get_bucket_object(bucket_name, object_key)
        if obj.type == "directory":
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)

    def generate_upload_url(
        self,
        bucket_name: str,
        target_key: str,
        raise_if_exists=False,
        host: str | None = None,
        *args,
        **kwargs,
    ):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        full_path = self.path(bucket_name, target_key)
        if self.exists(full_path) and raise_if_exists:
            raise self.exceptions.AlreadyExists(f"Object {target_key} already exist")

        token = self._create_token_for_payload(
            {"bucket_name": bucket_name, "file_path": target_key}
        )
        internal_url = reverse("files:upload_file", args=(token,))
        if host is None:
            host = settings.BASE_URL

        return f"{host}{internal_url}"

    def generate_download_url(
        self,
        bucket_name: str,
        target_key: str,
        force_attachment=False,
        host: str | None = None,
        *args,
        **kwargs,
    ):
        if not self.exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket {bucket_name} not found")
        full_path = self.path(bucket_name, target_key)
        if not self.exists(full_path):
            raise self.exceptions.NotFound(f"Object {target_key} not found")

        token = self._create_token_for_payload(
            {"bucket_name": bucket_name, "file_path": target_key}
        )
        endpoint = reverse("files:download_file", args=(token,))
        if force_attachment:
            endpoint += "?attachment=true"

        if host is None:
            host = settings.BASE_URL

        return f"{host}{endpoint}"

    def get_bucket_mount_config(self, bucket_name):
        return {
            "WORKSPACE_STORAGE_MOUNT_PATH": str(
                safe_join(
                    self.ext_bind_path if self.ext_bind_path else self.data_dir,
                    bucket_name,
                )
            ),
        }
