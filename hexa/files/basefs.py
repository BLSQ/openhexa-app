from abc import ABC, abstractmethod
import typing
from dataclasses import dataclass
from google.api_core.exceptions import NotFound

@dataclass
class ObjectsPage:
    items: typing.List[any]
    has_next_page: bool
    has_previous_page: bool
    page_number: int


class BaseClient(ABC):

    @abstractmethod
    def create_bucket(self, bucket_name: str):
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
        ignore_hidden_files=True,
    ):
        pass

    @abstractmethod
    def get_short_lived_downscoped_access_token(self, bucket_name):
        pass