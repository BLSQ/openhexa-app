import io
import os
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os.path import dirname, isfile, join

from .exceptions import AlreadyExists, NotFound, SuspiciousFileOperation


class BadRequest(Exception):
    pass


@dataclass
class ObjectsPage:
    items: typing.List[any]
    has_next_page: bool
    has_previous_page: bool
    page_number: int


def load_bucket_sample_data_with(bucket_name: str, client_storage):
    """
    Init bucket with default content
    """
    static_files_dir = join(dirname(__file__), "..", "static")
    files = [
        f for f in os.listdir(static_files_dir) if isfile(join(static_files_dir, f))
    ]

    for file in files:
        client_storage.save_object(
            bucket_name, file, open(join(static_files_dir, file), "rb")
        )


@dataclass
class StorageObject:
    name: str
    key: str
    path: str
    type: str
    updated: str = None
    size: int = 0
    content_type: str = None


class Storage(ABC):
    storage_type = None

    class exceptions:
        BadRequest = BadRequest
        NotFound = NotFound
        AlreadyExists = AlreadyExists
        SuspiciousFileOperation = SuspiciousFileOperation

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def bucket_exists(self, bucket_name: str):
        pass

    @abstractmethod
    def create_bucket(self, bucket_name: str, *args, **kwargs):
        pass

    @abstractmethod
    def delete_object(self, bucket_name: str, object_key: str):
        pass

    @abstractmethod
    def delete_bucket(self, bucket_name: str, force: bool = False):
        pass

    @abstractmethod
    def save_object(self, bucket_name: str, file_path: str, file: io.BufferedReader):
        pass

    @abstractmethod
    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        pass

    @abstractmethod
    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False, *args, **kwargs
    ):
        pass

    @abstractmethod
    def get_bucket_object(self, bucket_name: str, object_key: str):
        pass

    @abstractmethod
    def list_bucket_objects(
        self,
        bucket_name,
        prefix=None,
        page: int = 1,
        per_page=30,
        query=None,
        ignore_hidden_files=True,
    ):
        pass

    @abstractmethod
    def generate_upload_url(
        self,
        bucket_name: str,
        target_key: str,
        content_type: str,
        raise_if_exists=False,
        *args,
        **kwargs,
    ):
        pass

    @abstractmethod
    def get_bucket_mount_config(self, bucket_name):
        pass
