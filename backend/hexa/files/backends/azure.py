from datetime import datetime, timedelta, timezone

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
)
from azure.storage.blob import (
    BlobPrefix,
    BlobSasPermissions,
    BlobServiceClient,
    ContainerSasPermissions,
    generate_blob_sas,
    generate_container_sas,
)

from .base import ObjectsPage, Storage, StorageObject, load_bucket_sample_data_with


def _blob_to_obj(blob_properties, container_name):
    if isinstance(blob_properties, BlobPrefix):
        return StorageObject(
            name=blob_properties.name.rstrip("/").split("/")[-1],
            key=blob_properties.name,
            path=f"{container_name}/{blob_properties.name}",
            type="directory",
        )
    else:
        return StorageObject(
            name=blob_properties.name.split("/")[-1],
            path=f"{container_name}/{blob_properties.name}",
            key=blob_properties.name,
            content_type=blob_properties.content_settings.content_type,
            updated=blob_properties.last_modified.isoformat()
            if blob_properties.last_modified
            else None,
            size=blob_properties.size,
            type="file",
        )


class AzureBlobStorage(Storage):
    storage_type = "azure"

    def __init__(self, connection_string):
        super().__init__()
        self.connection_string = connection_string
        self.client = BlobServiceClient.from_connection_string(connection_string)

    def bucket_exists(self, bucket_name):
        try:
            return self.client.get_container_client(bucket_name).exists()
        except ResourceNotFoundError:
            return False

    def create_bucket(self, bucket_name, *args, **kwargs):
        try:
            bucket = self.client.create_container(bucket_name)
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
        # Create a key to a empty placeholder file used to create the folder
        folder_key = folder_key.rstrip("/") + "/"

        blob_client = self.client.get_blob_client(
            container=bucket_name, blob=folder_key + ".placeholder"
        )
        blob_client.upload_blob(b"", overwrite=True)

        blob = self.client.get_blob_client(container=bucket_name, blob=folder_key)
        return _blob_to_obj(blob.get_blob_properties(), bucket_name)

    def generate_download_url(
        self, bucket_name, target_key, expiration=3600, *args, **kwargs
    ):
        # Get a blob client for the target blob
        blob_client = self.client.get_blob_client(
            container=bucket_name, blob=target_key
        )

        # Update the start time and expiry time for SAS token
        sas_start_time = datetime.now(timezone.utc)
        sas_expiry_time = sas_start_time + timedelta(seconds=expiration)

        # Generate the Azure Blob Storage SAS token
        sas_token = generate_blob_sas(
            account_name=str(self.client.account_name),
            account_key=self.client.credential.account_key,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=sas_expiry_time,
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
        page: int = 1,
        per_page=30,
        query=None,
        ignore_hidden_files=True,
        **kwargs,
    ):
        """List objects in a Azure Blob Container

        Limitations:
            It cannot returns the list of objects matching a glob pattern. In order to implement such a feature,
            we would need to implement a Blob Indexer
            (https://learn.microsoft.com/en-us/azure/search/search-blob-storage-integration?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json&bc=%2Fazure%2Fstorage%2Fblobs%2Fbreadcrumb%2Ftoc.json)

            It's not possible to create a empty directory using the Azure SDK/API. To simulate it, we create a empty `.placeholder` blob and filter it out.

        Args:
            bucket_name (_type_): _description_
            prefix (_type_, optional): _description_. Defaults to None.
            page (int, optional): _description_. Defaults to 1.
            per_page (int, optional): _description_. Defaults to 30.
            query (_type_, optional): _description_. Defaults to None.
            ignore_hidden_files (bool, optional): _description_. Defaults to True.

        """
        iter_blobs = self.client.get_container_client(bucket_name).walk_blobs(
            name_starts_with=prefix, delimiter="/", results_per_page=per_page * 2
        )

        max_items = (page * per_page) + 1
        start_offset = (page - 1) * per_page
        end_offset = page * per_page

        objects = []

        def is_object_match_query(obj):
            # Filter out ".placeholder" files used to create folders
            if obj.name.endswith(".placeholder"):
                return False
            if ignore_hidden_files and obj.name.startswith("."):
                return False
            if query:
                return query.lower() in obj.name.lower()
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
        blob_client = self.client.get_blob_client(container=bucket_name, blob=file_name)
        blob_client.delete_blob()

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
