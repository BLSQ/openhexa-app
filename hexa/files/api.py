import typing
from dataclasses import dataclass
from .gcp import GCPClient
from .s3 import S3Client

import os
import typing
from os.path import dirname, isfile, join
from warnings import warn
from .basefs import NotFound

default_mode = "s3"

mode = default_mode

def get_client(mode=default_mode):
    if mode == "gcp":
        return GCPClient()
    if mode == "s3":
        return S3Client()
    raise Exception(f"unsupported filesystem {mode}")


def create_bucket(bucket_name):
    warn(
        "This is deprecated use get_client().create_bucket(...); version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
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
    warn(
        "This is deprecated use get_client().create_bucket_folder(...);; version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_client().create_bucket_folder(bucket_name, folder_key)


def delete_object(bucket_name, name):
    warn(
        "This is deprecated use get_client().delete_object(...);; version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_client().delete_object(bucket_name, name)


def generate_download_url(bucket_name: str, target_key: str, force_attachment=False):
    warn(
        "This is deprecated use get_client().generate_download_url(...);; version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_client().generate_download_url(bucket_name, target_key, force_attachment)


def generate_upload_url(
    bucket_name: str, target_key: str, content_type: str, raise_if_exists=False
):
    warn(
        "This is deprecated use get_client().generate_upload_url(...);; version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_client().generate_upload_url(
        bucket_name, target_key, content_type, raise_if_exists
    )


def get_bucket_object(bucket_name: str, object_key: str):
    warn(
        "This is deprecated use get_client().get_bucket_object(...);; version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_client().get_bucket_object(bucket_name, object_key)


def list_bucket_objects(
    bucket_name, prefix=None, page: int = 1, per_page=30, ignore_hidden_files=True
):
    warn(
        "This is deprecated use get_client().list_bucket_objects(...);; version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_client().list_bucket_objects(
        bucket_name, prefix, page, per_page, ignore_hidden_files
    )


def get_short_lived_downscoped_access_token(bucket_name):
    warn(
        "This is deprecated use get_client().get_short_lived_downscoped_access_token(...);; version=1.0.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_client().get_short_lived_downscoped_access_token(bucket_name)
