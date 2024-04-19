import base64
import json

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from google.cloud import storage
from google.cloud.exceptions import Conflict
from google.cloud.iam_credentials_v1 import IAMCredentialsClient
from google.cloud.storage.blob import Blob
from google.oauth2 import service_account
from google.protobuf import duration_pb2

from .basefs import BaseClient, NotFound, ObjectsPage, load_bucket_sample_data_with


def get_credentials():
    decoded_creds = base64.b64decode(settings.GCS_SERVICE_ACCOUNT_KEY)
    json_creds = json.loads(decoded_creds, strict=False)
    return service_account.Credentials.from_service_account_info(json_creds)


def get_storage_client():
    credentials = get_credentials()
    return storage.Client(credentials=credentials)


def _is_dir(blob):
    return blob.size == 0 and blob.name.endswith("/")


def _blob_to_dict(blob: Blob):
    return {
        "name": blob.name.split("/")[-2] if _is_dir(blob) else blob.name.split("/")[-1],
        "key": blob.name,
        "path": "/".join([blob.bucket.name, blob.name]),
        "content_type": blob.content_type,
        "updated": blob.updated,
        "size": blob.size,
        "type": "directory" if _is_dir(blob) else "file",
    }


def _prefix_to_dict(bucket_name, name: str):
    return {
        "name": name.split("/")[-2],
        "key": name,
        "path": "/".join([bucket_name, name]),
        "size": 0,
        "type": "directory",
    }


def iter_request_results(bucket_name, request):
    # Start by adding all the prefixes
    # Prefixes are virtual directories based on the delimiter specified in the request
    # The API returns a list of keys that have the delimiter as a suffix (meaning they have objects in them)

    # request.prefixes is a Set (unorder) so to keep the prefixes order we need to sort them
    pages = request.pages
    prefixes = request.prefixes

    current_page = next(pages)

    for prefix in sorted(prefixes):
        yield _prefix_to_dict(bucket_name, prefix)

    while True:
        for blob in current_page:
            if not _is_dir(blob):
                # We ignore objects that are directories (object with a size = 0 and ending with a /)
                # because they are already listed in the prefixes
                yield _blob_to_dict(blob)
        try:
            current_page = next(pages)
        except StopIteration:
            return


def ensure_is_folder(object_key: str):
    if object_key.endswith("/") is False:
        return object_key + "/"
    return object_key


class GCPClient(BaseClient):
    def create_bucket(self, bucket_name: str):
        client = get_storage_client()
        try:
            bucket = client.create_bucket(
                bucket_name, location=settings.WORKSPACE_BUCKET_REGION
            )
            bucket.storage_class = "STANDARD"  # Default storage class

            if settings.WORKSPACE_BUCKET_VERSIONING_ENABLED:
                bucket.versioning_enabled = True

            # Set lifecycle rules
            # 1. Transition to "Nearline" Storage: Objects that haven't been accessed for 30 days can be moved to "Nearline" storage, which is cost-effective for data accessed less than once a month.
            # 2. Transition to "Coldline" Storage: For objects that are less frequently accessed, moving them to "Coldline" storage after 90 days can further reduce costs. "Coldline" is suitable for accessing data at most once a quarter.
            # 3. Transition to "Archive" Storage: Cost-effective storage class for long-term preservation of data that's accessed less than once a year is Archive. Transition objects to "Archive" storage after 365 days.
            # 4. Version Control: Keep only the 3 most recent versions of each object to prevent unnecessary storage costs while ensuring the availability of previous versions for a limited time.
            # 5. Delete Old Noncurrent Versions: Remove noncurrent versions of objects that are older than 365 days.
            bucket.lifecycle_rules = [
                {
                    "action": {
                        "type": "SetStorageClass",
                        "storageClass": "NEARLINE",
                    },
                    "condition": {"age": 30},
                },
                {
                    "action": {
                        "type": "SetStorageClass",
                        "storageClass": "COLDLINE",
                    },
                    "condition": {"age": 90},
                },
                {
                    "action": {
                        "type": "SetStorageClass",
                        "storageClass": "ARCHIVE",
                    },
                    "condition": {"age": 365},
                },
                {
                    "action": {"type": "Delete"},
                    "condition": {"isLive": False, "numNewerVersions": 3},
                },
            ]
            bucket.cors = [
                {
                    "origin": settings.CORS_ALLOWED_ORIGINS,
                    "responseHeader": [
                        "Authorization",
                        "Content-Range",
                        "Accept",
                        "Content-Type",
                        "Origin",
                        "Range",
                    ],
                    "method": ["GET", "PUT"],
                    "maxAgeSeconds": 3600,
                }
            ]
            bucket.patch()

            return bucket
        except Conflict:
            raise ValidationError(f"GCS: Bucket {bucket_name} already exists!")

    def upload_object(self, bucket_name: str, file_name: str, source: str):
        client = get_storage_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_filename(source)

    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        client = get_storage_client()
        bucket = client.get_bucket(bucket_name)
        object = bucket.blob(ensure_is_folder(folder_key))
        object.upload_from_string(
            "", content_type="application/x-www-form-urlencoded;charset=UTF-8"
        )

        return _blob_to_dict(object)

    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False
    ):
        client = get_storage_client()
        gcs_bucket = client.get_bucket(bucket_name)
        blob: Blob = gcs_bucket.get_blob(target_key)

        if blob is None:
            return None

        filename = blob.name.split("/")[-1]

        response_disposition = (
            f"attachment;filename={filename}" if force_attachment else None
        )

        return blob.generate_signed_url(
            expiration=600, version="v4", response_disposition=response_disposition
        )

    def generate_upload_url(
        self,
        bucket_name: str,
        target_key: str,
        content_type: str = None,
        raise_if_exists: bool = False,
    ):
        client = get_storage_client()
        gcs_bucket = client.get_bucket(bucket_name)
        if raise_if_exists and gcs_bucket.get_blob(target_key) is not None:
            raise ValidationError(f"GCS: Object {target_key} already exists!")
        blob = gcs_bucket.blob(target_key)
        return blob.generate_signed_url(
            expiration=3600, version="v4", method="PUT", content_type=content_type
        )

    def get_bucket_object(self, bucket_name: str, object_key: str):
        client = get_storage_client()
        bucket = client.get_bucket(bucket_name)
        object = bucket.get_blob(object_key)
        if object is None:
            raise NotFound("Object not found")

        return _blob_to_dict(object)

    def list_bucket_objects(
        self,
        bucket_name,
        prefix=None,
        page: int = 1,
        per_page=30,
        query=None,
        ignore_delimiter=False,
        ignore_hidden_files=True,
    ):
        """Returns the list of objects in a bucket with pagination support.
        Objects starting with a dot can be ignored using `ignore_hidden_files`.

        Args:
            bucket_name (str): Bucket name
            prefix (str, optional): The prefix the keys of the objects must have to be returned. Defaults to None.
            page (int, optional): Page to return. Defaults to 1.
            per_page (int, optional): Items per page. Defaults to 30.
            query (str, optional): Query to filter the objects. Defaults to None.
            ignore_hidden_files (bool, optional): Returns the hidden files and directories if `False`. Defaults to True.

        """
        client = get_storage_client()

        request = client.list_blobs(
            bucket_name,
            prefix=prefix,
            # We take twice the number of items to be sure to have enough
            page_size=per_page * 2,
            delimiter="" if ignore_delimiter else "/",
            include_trailing_delimiter=True,
        )
        max_items = (page * per_page) + 1
        start_offset = (page - 1) * per_page
        end_offset = page * per_page

        objects = []

        def is_object_match_query(obj):
            if ignore_hidden_files and obj["name"].startswith("."):
                return False
            if not query:
                return True
            return query.lower() in obj["name"].lower()

        iterator = iter_request_results(bucket_name, request)
        while True:
            try:
                obj = next(iterator)
                if is_object_match_query(obj):
                    objects.append(obj)

                if len(objects) >= max_items:
                    # We have enough items, let's stop the loop
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
            has_next_page=len(objects) > page * per_page,
        )

    # TODO handle read-only mode.
    def get_short_lived_downscoped_access_token(self, bucket_name):
        token_lifetime = 3600
        if settings.GCS_TOKEN_LIFETIME is not None:
            token_lifetime = int(settings.GCS_TOKEN_LIFETIME)
        source_credentials = get_credentials()

        iam_credentials = IAMCredentialsClient(credentials=source_credentials)
        iam_token = iam_credentials.generate_access_token(
            name=f"projects/-/serviceAccounts/{source_credentials._service_account_email}",
            scope=["https://www.googleapis.com/auth/devstorage.full_control"],
            lifetime=duration_pb2.Duration(seconds=token_lifetime),
        )
        # We call directly the REST API because the Python client library does
        # not support to createe a downscoped token with a extended lifetime
        # (Or we didn't find how...)
        response = requests.post(
            "https://sts.googleapis.com/v1/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "subject_token": iam_token.access_token,
                "options": json.dumps(
                    {
                        "accessBoundary": {
                            "accessBoundaryRules": [
                                {
                                    "availableResource": f"//storage.googleapis.com/projects/_/buckets/{bucket_name}",
                                    "availablePermissions": [
                                        "inRole:roles/storage.objectAdmin"
                                    ],
                                }
                            ]
                        }
                    }
                ),
            },
        )
        payload = response.json()
        return [payload["access_token"], payload["expires_in"], "gcp"]

    def delete_bucket(self, bucket_name: str, fully: bool = False):
        return get_storage_client().delete_bucket(bucket_name)

    def delete_object(self, bucket_name: str, file_name: str):
        client = get_storage_client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.get_blob(file_name)
        if _is_dir(blob):
            blobs = list(bucket.list_blobs(prefix=file_name))
            bucket.delete_blobs(blobs)
        else:
            bucket.delete_blob(file_name)
        return

    def load_bucket_sample_data(self, bucket_name: str):
        return load_bucket_sample_data_with(bucket_name, self)

    def get_token_as_env_variables(self, token):
        return {
            "GCS_TOKEN": token,  # FIXME: Once we have deployed the new openhexa-bslq-environment image and upgraded the openhexa-app, we can remove this line
            "WORKSPACE_STORAGE_ENGINE_GCP_ACCESS_TOKEN": token,
        }
