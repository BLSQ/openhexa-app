import typing
from dataclasses import dataclass
from .gcp import GCPClient
from .s3 import S3Client
from google.api_core.exceptions import NotFound
import os
import typing
from os.path import dirname, isfile, join


@dataclass
class ObjectsPage:
    items: typing.List[any]
    has_next_page: bool
    has_previous_page: bool
    page_number: int


mode = "s3"
client = GCPClient

if mode == "s3":
    client = S3Client


def get_client():
    return client


def create_bucket(bucket_name):
    return get_client().create_bucket(bucket_name)


def load_bucket_sample_data(bucket_name: str):
    """
    Init bucket with default content
    """
    static_files_dir = join(dirname(__file__), "static")
    files = [
        f for f in os.listdir(static_files_dir) if isfile(join(static_files_dir, f))
    ]
    storage = get_client()
    for file in files:
        storage.upload_object(bucket_name, file, join(static_files_dir, file))


def create_bucket_folder(bucket_name: str, folder_key: str):
    return get_client().create_bucket_folder(bucket_name, folder_key)


def delete_object(bucket_name, name):
    return get_client().delete_object(bucket_name, name)


def generate_download_url(bucket_name: str, target_key: str, force_attachment=False):
    return get_client().generate_download_url(bucket_name, target_key, force_attachment)


def generate_upload_url(
    bucket_name: str, target_key: str, content_type: str, raise_if_exists=False
):
    return get_client().generate_upload_url(
        bucket_name, target_key, content_type, raise_if_exists
    )


def get_bucket_object(bucket_name: str, object_key: str):
    return get_client().get_bucket_object(bucket_name, object_key)


def list_bucket_objects(
    bucket_name, prefix=None, page: int = 1, per_page=30, ignore_hidden_files=True
):
    return get_client().list_bucket_objects(
        bucket_name, prefix, page, per_page, ignore_hidden_files
    )


def get_short_lived_downscoped_access_token(bucket_name):
    return get_client().get_short_lived_downscoped_access_token(bucket_name)
