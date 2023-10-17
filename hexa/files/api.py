import base64
import json
import os
import typing
from dataclasses import dataclass
from os.path import dirname, isfile, join

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from google.api_core.exceptions import NotFound
from google.cloud import storage
from google.cloud.exceptions import Conflict
from google.cloud.iam_credentials_v1 import IAMCredentialsClient
from google.cloud.storage.blob import Blob
from google.oauth2 import service_account
from google.protobuf import duration_pb2


@dataclass
class ObjectsPage:
    items: typing.List[any]
    has_next_page: bool
    has_previous_page: bool
    page_number: int


def get_credentials():
    decoded_creds = base64.b64decode(settings.GCS_SERVICE_ACCOUNT_KEY)
    json_creds = json.loads(decoded_creds, strict=False)
    return service_account.Credentials.from_service_account_info(json_creds)


def get_short_lived_downscoped_access_token(bucket_name):
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
    return payload["access_token"], payload["expires_in"]


def get_storage_client():
    credentials = get_credentials()
    return storage.Client(credentials=credentials)


def _is_dir(blob):
    return blob.size == 0 and blob.name.endswith("/")


def create_bucket(bucket_name):
    client = get_storage_client()
    try:
        bucket = client.create_bucket(
            bucket_name, location=settings.WORKSPACE_BUCKET_REGION
        )
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
    except Conflict as e:
        raise ValidationError(f"GCS: Bucket {bucket_name} already exists!")


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


def list_bucket_objects(
    bucket_name, prefix=None, page: int = 1, per_page=30, ignore_hidden_files=True
):
    """Returns the list of objects in a bucket with pagination support.
    Objects starting with a dot can be ignored using `ignore_hidden_files`.

    Args:
        bucket_name (str): Bucket name
        prefix (str, optional): The prefix the keys of the objects must have to be returned. Defaults to None.
        page (int, optional): Page to return. Defaults to 1.
        per_page (int, optional): Items per page. Defaults to 30.
        ignore_hidden_files (bool, optional): Returns the hidden files and directories if `False`. Defaults to True.

    """
    client = get_storage_client()

    request = client.list_blobs(
        bucket_name,
        prefix=prefix,
        # We take twice the number of items to be sure to have enough
        page_size=per_page * 2,
        delimiter="/",
        include_trailing_delimiter=True,
    )
    pages = request.pages

    max_items = (page * per_page) + 1
    start_offset = (page - 1) * per_page
    end_offset = page * per_page

    objects = []
    try:
        current_page = next(pages)

        # Start by adding all the prefixes
        # Prefixes are virtual directories based on the delimiter specified in the request
        # The API returns a list of keys that have the delimiter as a suffix (meaning they have objects in them)

        # request.prefixes is a Set (unorder) so to keep the prefixes order we need to sort them
        prefixes = sorted(request.prefixes)
        for prefix in prefixes:
            res = _prefix_to_dict(bucket_name, prefix)
            if not ignore_hidden_files or not res["name"].startswith("."):
                objects.append(res)

        while True:
            for obj in current_page:
                if _is_dir(obj):
                    # We ignore objects that are directories (object with a size = 0 and ending with a /)
                    # because they are already listed in the prefixes
                    continue

                res = _blob_to_dict(obj)
                if not ignore_hidden_files or not res["name"].startswith("."):
                    objects.append(res)

            if len(objects) >= max_items:
                # We have enough items, let's break
                break

            # Otherwise we load the next page and continue our loop
            current_page = next(pages)

        return ObjectsPage(
            items=objects[start_offset:end_offset],
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=len(objects) > page * per_page,
        )

    except StopIteration:
        # We reached the end of the list of pages. Let's return what we have and set the
        # has_next_page to false
        return ObjectsPage(
            items=objects[start_offset:end_offset],
            page_number=page,
            has_previous_page=page > 1,
            has_next_page=False,
        )


def ensure_is_folder(object_key: str):
    if object_key.endswith("/") is False:
        return object_key + "/"
    return object_key


def get_bucket_object(bucket_name: str, object_key: str):
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    object = bucket.get_blob(object_key)
    if object is None:
        raise NotFound("Object not found")

    return _blob_to_dict(object)


def create_bucket_folder(bucket_name: str, folder_key: str):
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    object = bucket.blob(ensure_is_folder(folder_key))
    object.upload_from_string(
        "", content_type="application/x-www-form-urlencoded;charset=UTF-8"
    )

    return _blob_to_dict(object)


def delete_object(bucket_name, name):
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(name)
    if _is_dir(blob):
        blobs = list(bucket.list_blobs(prefix=name))
        bucket.delete_blobs(blobs)
    else:
        bucket.delete_blob(name)
    return


def generate_download_url(bucket_name: str, target_key: str, force_attachment=False):
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
    bucket_name: str, target_key: str, content_type: str, raise_if_exists=False
):
    client = get_storage_client()
    gcs_bucket = client.get_bucket(bucket_name)
    if raise_if_exists and gcs_bucket.get_blob(target_key) is not None:
        raise ValidationError(f"GCS: Object {target_key} already exists!")
    blob = gcs_bucket.blob(target_key)
    return blob.generate_signed_url(
        expiration=3600, version="v4", method="PUT", content_type=content_type
    )


def load_bucket_sample_data(bucket_name: str):
    """
    Init bucket with default content
    """
    static_files_dir = join(dirname(__file__), "static")
    files = [
        f for f in os.listdir(static_files_dir) if isfile(join(static_files_dir, f))
    ]
    for file in files:
        upload_object(bucket_name, file, join(static_files_dir, file))


def upload_object(bucket_name: str, file_name: str, source: str):
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(source)
