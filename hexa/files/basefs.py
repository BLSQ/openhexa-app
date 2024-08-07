import os
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os.path import dirname, isfile, join


class NotFound(Exception):
    pass


class BucketObjectAlreadyExists(Exception):
    def __init__(self, target_key):
        self.message = (
            f"File already exists. Choose a different object key {target_key}."
        )
        super().__init__(self.message)


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
    static_files_dir = join(dirname(__file__), "static")
    files = [
        f for f in os.listdir(static_files_dir) if isfile(join(static_files_dir, f))
    ]

    for file in files:
        client_storage.upload_object(bucket_name, file, join(static_files_dir, file))


class BaseClient(ABC):
    class exceptions:
        NotFound = NotFound

    @abstractmethod
    def create_bucket(self, bucket_name: str, *args, **kwargs):
        pass

    @abstractmethod
    def delete_bucket(self, bucket_name: str, fully: bool = False):
        pass

    @abstractmethod
    def upload_object(self, bucket_name: str, file_name: str, source: str):
        pass

    @abstractmethod
    def create_bucket_folder(self, bucket_name: str, folder_key: str):
        pass

    @abstractmethod
    def generate_download_url(
        self, bucket_name: str, target_key: str, force_attachment=False
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
    def get_short_lived_downscoped_access_token(self, bucket_name):
        pass

    @abstractmethod
    def generate_upload_url(
        self,
        bucket_name: str,
        target_key: str,
        content_type: str,
        raise_if_exists=False,
    ):
        pass

    @abstractmethod
    def get_token_as_env_variables(self, token):
        pass
