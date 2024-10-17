import io

from .base import ObjectsPage, Storage, StorageObject

dummy_buckets = {}


class DummyStorageClient(Storage):
    storage_type = "dummy"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def buckets(self):
        return dummy_buckets

    def reset(self):
        dummy_buckets.clear()

    def bucket_exists(self, bucket_name: str):
        # Mock checking if the bucket exists
        return bucket_name in dummy_buckets

    def create_bucket(self, bucket_name: str, *args, **kwargs):
        # Mock bucket creation
        if bucket_name in dummy_buckets:
            raise self.exceptions.AlreadyExists(
                f"Bucket '{bucket_name}' already exists."
            )
        dummy_buckets[bucket_name] = {}
        return bucket_name

    def delete_object(self, bucket_name: str, object_key: str):
        # Mock object deletion
        if (
            bucket_name not in dummy_buckets
            or object_key not in dummy_buckets[bucket_name]
        ):
            raise self.exceptions.NotFound(
                f"Object '{object_key}' not found in bucket '{bucket_name}'."
            )
        del dummy_buckets[bucket_name][object_key]

    def delete_bucket(self, bucket_name: str, force: bool = False):
        # Mock bucket deletion
        if bucket_name not in dummy_buckets:
            raise self.exceptions.NotFound(f"Bucket '{bucket_name}' not found.")
        if force is False and dummy_buckets[bucket_name]:
            raise self.exceptions.BadRequest(f"Bucket '{bucket_name}' is not empty.")
        del dummy_buckets[bucket_name]

    def save_object(self, bucket_name: str, file_path: str, file: io.BufferedReader):
        # Mock saving an object in a bucket
        if bucket_name not in dummy_buckets:
            raise self.exceptions.NotFound(f"Bucket '{bucket_name}' not found.")
        dummy_buckets[bucket_name][file_path] = file.read()

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        # Mock creating a folder in a bucket
        if bucket_name not in dummy_buckets:
            raise self.exceptions.NotFound(f"Bucket '{bucket_name}' not found.")
        if folder_key in dummy_buckets[bucket_name]:
            raise self.exceptions.AlreadyExists(
                f"Folder '{folder_key}' already exists."
            )
        dummy_buckets[bucket_name][folder_key] = {}

    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False, *args, **kwargs
    ):
        # Mock generating a download URL
        if (
            bucket_name not in dummy_buckets
            or target_key not in dummy_buckets[bucket_name]
        ):
            raise self.exceptions.NotFound(
                f"Object '{target_key}' not found in bucket '{bucket_name}'."
            )
        return f"http://mockstorage.com/{bucket_name}/{target_key}"

    def _to_storage_object(self, bucket_name: str, object_key: str):
        if not self.bucket_exists(bucket_name):
            raise self.exceptions.NotFound(f"Bucket '{bucket_name}' not found.")
        if object_key not in dummy_buckets[bucket_name]:
            raise self.exceptions.NotFound(
                f"Object '{object_key}' not found in bucket '{bucket_name}'."
            )
        obj = dummy_buckets[bucket_name][object_key]
        if obj == {}:
            return StorageObject(
                name=object_key.split("/")[-1],
                key=object_key,
                path=f"{bucket_name}/{object_key}",
                updated="",
                type="directory",
            )
        else:
            return StorageObject(
                name=object_key.split("/")[-1],
                key=object_key,
                path=f"{bucket_name}/{object_key}",
                updated="",
                type="file",
                size=len(obj),
            )

    def get_bucket_object(self, bucket_name: str, object_key: str):
        # Mock retrieving an object from a bucket
        if (
            bucket_name not in dummy_buckets
            or object_key not in dummy_buckets[bucket_name]
        ):
            raise self.exceptions.NotFound(
                f"Object '{object_key}' not found in bucket '{bucket_name}'."
            )
        return self._to_storage_object(bucket_name, object_key)

    def list_bucket_objects(
        self,
        bucket_name,
        prefix=None,
        page: int = 1,
        per_page=30,
        query=None,
        ignore_hidden_files=True,
    ):
        # Mock listing objects in a bucket
        if bucket_name not in dummy_buckets:
            raise self.exceptions.NotFound(f"Bucket '{bucket_name}' not found.")
        object_keys = []
        for key in dummy_buckets[bucket_name].keys():
            if key.startswith(prefix or "") and (not query or query in key):
                object_keys.append(key)

        start = (page - 1) * per_page
        end = start + per_page
        objects = [
            self._to_storage_object(bucket_name, key) for key in object_keys[start:end]
        ]
        return ObjectsPage(
            items=objects,
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=end < len(objects),
        )

    def generate_upload_url(
        self,
        bucket_name: str,
        target_key: str,
        content_type: str,
        raise_if_exists=False,
        *args,
        **kwargs,
    ):
        # Mock generating an upload URL
        if bucket_name not in dummy_buckets:
            raise self.exceptions.NotFound(f"Bucket '{bucket_name}' not found.")
        if raise_if_exists and target_key in dummy_buckets[bucket_name]:
            raise self.exceptions.AlreadyExists(
                f"Object '{target_key}' already exists."
            )
        return f"http://mockstorage.com/{bucket_name}/{target_key}/upload"

    def get_bucket_mount_config(self, bucket_name):
        # Mock retrieving bucket mount config
        if bucket_name not in dummy_buckets:
            raise self.exceptions.NotFound(f"Bucket '{bucket_name}' not found.")
        return {}
