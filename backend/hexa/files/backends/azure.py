import fnmatch
from datetime import datetime, timedelta, timezone

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
)
from azure.storage.blob import (
    BlobPrefix,
    BlobProperties,
    BlobSasPermissions,
    BlobServiceClient,
    ContainerSasPermissions,
    generate_blob_sas,
    generate_container_sas,
)

from .base import ObjectsPage, Storage, StorageObject, load_bucket_sample_data_with


def _is_dir(blob_properties: BlobProperties | BlobPrefix) -> bool:
    return (
        isinstance(blob_properties, BlobPrefix)
        or blob_properties.metadata.get("hdi_isfolder", "false") == "true"
    )


def _blob_to_obj(blob_properties, container_name):
    if _is_dir(blob_properties):
        return StorageObject(
            name=blob_properties.name.rstrip("/").split("/")[-1],
            key=blob_properties.name,
            path=f"{container_name}/{blob_properties.name}",
            type="directory",
        )
    else:
        updated_at = (
            blob_properties.last_modified.isoformat()
            if blob_properties.last_modified
            else None
        )
        return StorageObject(
            name=blob_properties.name.split("/")[-1],
            path=f"{container_name}/{blob_properties.name}",
            key=blob_properties.name,
            content_type=blob_properties.content_settings.content_type,
            updated_at=updated_at,
            size=blob_properties.size,
            type="file",
        )


class AzureBlobStorage(Storage):
    storage_type = "azure"
    folder_placeholder = ".keep"

    def __init__(self, connection_string):
        super().__init__()
        self.connection_string = connection_string
        self.client = BlobServiceClient.from_connection_string(connection_string)

    def bucket_exists(self, bucket_name):
        try:
            return self.client.get_container_client(bucket_name).exists()
        except ResourceNotFoundError:
            return False

    def create_bucket(self, bucket_name, labels=None, *args, **kwargs):
        try:
            bucket = self.client.create_container(bucket_name, metadata=labels)
            return bucket.container_name
        except ResourceExistsError:
            raise Storage.exceptions.AlreadyExists(
                f"Bucket {bucket_name} already exists"
            )
        except HttpResponseError as e:
            raise Storage.exceptions.BadRequest(
                f"Cannot create the bucket {bucket_name}: {e.message}"
            ) from e

    def save_object(self, bucket_name, file_path, file):
        blob_client = self.client.get_blob_client(container=bucket_name, blob=file_path)
        blob_client.upload_blob(file, overwrite=True)

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        folder_key = folder_key.rstrip("/") + "/"

        blob_client = self.client.get_blob_client(
            container=bucket_name, blob=folder_key + self.folder_placeholder
        )
        blob_client.upload_blob(b"", overwrite=True)

        return StorageObject(
            name=folder_key.rstrip("/").split("/")[-1],
            key=folder_key,
            path=f"{bucket_name}/{folder_key}",
            type="directory",
        )

    def generate_download_url(
        self,
        *,
        bucket_name,
        target_key,
        force_attachment=False,
        expiration=3600,
        **kwargs,
    ):
        # Get a blob client for the target blob
        blob_client = self.client.get_blob_client(
            container=bucket_name, blob=target_key
        )

        # Update the start time and expiry time for SAS token
        sas_start_time = datetime.now(timezone.utc)
        sas_expiry_time = sas_start_time + timedelta(seconds=expiration)

        # Set content disposition to force download if requested
        filename = blob_client.blob_name.split("/")[-1]
        content_disposition = (
            f"attachment; filename={filename}" if force_attachment else None
        )

        # Generate the Azure Blob Storage SAS token
        sas_token = generate_blob_sas(
            account_name=str(self.client.account_name),
            account_key=self.client.credential.account_key,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=sas_expiry_time,
            content_disposition=content_disposition,
        )

        return f"{blob_client.url}?{sas_token}"

    def generate_upload_url(
        self, *, bucket_name, target_key, content_type=None, expiration=3600, **kwargs
    ):
        # Get a blob client for the target blob
        blob_client = self.client.get_blob_client(
            container=bucket_name, blob=target_key
        )

        # Update the start time and expiry time for SAS token
        sas_start_time = datetime.now(timezone.utc)
        sas_expiry_time = sas_start_time + timedelta(seconds=expiration)

        # Update the right permissions for your SAS token
        sas_permissions = BlobSasPermissions(
            create=True, write=True, list=False, delete=False, read=False
        )

        # Generate the Azure Blob Storage SAS token
        sas_token = generate_blob_sas(
            account_name=str(self.client.account_name),
            account_key=self.client.credential.account_key,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            permission=sas_permissions,
            start=sas_start_time,
            expiry=sas_expiry_time,
        )

        headers = {
            "x-ms-blob-type": "BlockBlob",
        }
        if content_type:
            headers["Content-Type"] = content_type

        return f"{blob_client.url}?{sas_token}", headers

    def read_object(self, bucket_name: str, file_path: str) -> bytes:
        blob_client = self.client.get_blob_client(container=bucket_name, blob=file_path)
        return blob_client.download_blob().readall()

    def get_bucket_object(self, bucket_name, object_key):
        blob_client = self.client.get_blob_client(
            container=bucket_name, blob=object_key
        )
        try:
            blob_properties = blob_client.get_blob_properties()
            return _blob_to_obj(blob_properties, bucket_name)
        except ResourceNotFoundError:
            return None

    def list_bucket_objects(
        self,
        bucket_name,
        prefix=None,
        match_glob=None,
        page: int = 1,
        per_page=30,
        query=None,
        ignore_hidden_files=True,
    ):
        """List objects in a Azure Blob Container

        Limitations:
            Azure Blob Storage does not support server-side glob filtering. Glob matching is done
            client-side using fnmatch after listing all blobs. This may be slow on containers with
            many files, as it requires iterating through all blobs under the prefix.

            It's not possible to create a empty directory using the Azure SDK/API. To simulate it, we create a empty `.keep` blob and filter it out.

        """
        container_client = self.client.get_container_client(bucket_name)

        if match_glob:
            iter_blobs = container_client.list_blobs(
                name_starts_with=prefix, results_per_page=per_page * 2
            )
        else:
            iter_blobs = container_client.walk_blobs(
                name_starts_with=prefix, delimiter="/", results_per_page=per_page * 2
            )

        max_items = (page * per_page) + 1
        start_offset = (page - 1) * per_page
        end_offset = page * per_page

        objects = []

        lower_match_glob = match_glob.lower() if match_glob else None

        def is_object_match_query(obj):
            lower_name = obj.name.lower()
            # Filter out ".keep" files used to create folders
            if lower_name.endswith(self.folder_placeholder):
                return False
            if ignore_hidden_files and any(
                part.startswith(".") for part in lower_name.split("/")
            ):
                return False
            if query and query.lower() not in lower_name:
                return False
            if lower_match_glob and not fnmatch.fnmatch(lower_name, lower_match_glob):
                return False
            return True

        while True:
            try:
                obj = next(iter_blobs)
                if is_object_match_query(obj):
                    objects.append(_blob_to_obj(obj, bucket_name))

                if len(objects) >= max_items:
                    break
            except StopIteration:
                # We reached the end of the list of pages. Let's return what we have and set the
                # has_next_page to false
                return ObjectsPage(
                    items=objects[start_offset:end_offset],
                    page_number=page,
                    has_previous_page=page > 1,
                    has_next_page=False,
                )

        return ObjectsPage(
            items=objects[start_offset:end_offset],
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=len(objects) > end_offset,
        )

    def delete_object(self, bucket_name, file_name):
        container_client = self.client.get_container_client(container=bucket_name)

        def _delete_object(blob_name: str):
            blob_client = container_client.get_blob_client(blob=blob_name)
            if not _is_dir(blob_client.get_blob_properties()):
                blob_client.delete_blob()
            else:
                # As it's not possible to delete folders that are no empty, we first need to delete all files and folders inside the folder
                for blob_properties in container_client.walk_blobs(
                    delimiter="/", name_starts_with=blob_name
                ):
                    _delete_object(blob_properties.name)

        return _delete_object(file_name)

    def delete_bucket(self, bucket_name, force: bool = False):
        self.client.delete_container(bucket_name)

    def get_short_lived_access_token(self, bucket_name):
        sas_token = generate_container_sas(
            account_name=self.client.account_name,
            account_key=self.client.credential.account_key,
            container_name=bucket_name,
            permission=ContainerSasPermissions(
                read=True,
                list=True,
                write=True,
                delete=True,
                tag=True,
                filter=True,
                add=True,
                create=True,
                move=True,
                execute=True,
            ),
            expiry=datetime.now(timezone.utc) + timedelta(hours=12),
        )
        return sas_token

    def get_bucket_mount_config(self, bucket_name):
        return {
            "WORKSPACE_STORAGE_ENGINE_AZURE_ACCOUNT_NAME": self.client.account_name,
            "WORKSPACE_STORAGE_ENGINE_AZURE_STORAGE_SAS_TOKEN": self.get_short_lived_access_token(
                bucket_name
            ),
        }

    def load_bucket_sample_data(self, bucket_name: str):
        # This method is not implemented in the original code
        return load_bucket_sample_data_with(bucket_name, self)  #
