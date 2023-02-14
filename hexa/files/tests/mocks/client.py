from unittest import mock

from google.api_core import page_iterator
from google.cloud.exceptions import Conflict, NotFound

from .bucket import MockBucket


class MockClient:
    def __init__(
        self,
        backend,
        credentials=None,
        _http=None,
        client_info=None,
        client_options=None,
        *args,
        **kwargs,
    ):
        self.backend = backend
        self.project = backend.project
        self.credentials = credentials
        self._http = _http
        self.client_info = client_info
        self.client_options = client_options

    @classmethod
    def create_anonymous_client(cls):
        raise NotImplementedError

    @property
    def _connection(self):
        raise NotImplementedError

    @_connection.setter
    def _connection(self, value):
        raise NotImplementedError

    def _push_batch(self, batch):
        raise NotImplementedError

    def _pop_batch(self):
        raise NotImplementedError

    def _bucket_arg_to_bucket(self, bucket_or_name):
        if isinstance(bucket_or_name, MockBucket):
            bucket = bucket_or_name
        else:
            bucket = MockBucket(self, name=bucket_or_name)
        return bucket

    @property
    def current_batch(self):
        raise NotImplementedError

    def get_service_account_email(self, project=None):
        raise NotImplementedError

    def bucket(self, bucket_name, user_project=None):
        return MockBucket(client=self, name=bucket_name, user_project=user_project)

    def batch(self):
        raise NotImplementedError

    def get_bucket(self, bucket_or_name):
        bucket = self._bucket_arg_to_bucket(bucket_or_name)

        # TODO: Use bucket.reload(client=self) when MockBucket class is implemented
        if bucket.name in self.backend.buckets.keys():
            return self.backend.buckets[bucket.name]
        else:
            raise NotFound(
                "404 GET https://storage.googleapis.com/storage/v1/b/{}?projection=noAcl".format(
                    bucket.name
                )
            )

    def lookup_bucket(self, bucket_name):
        try:
            return self.get_bucket(bucket_name)
        except NotFound:
            return None

    def create_bucket(self, bucket_or_name, requester_pays=None, project=None):
        bucket = self._bucket_arg_to_bucket(bucket_or_name)
        # bucket.create(client=self, project=project)
        if bucket.name in self.backend.buckets.keys():
            raise Conflict(
                "409 POST https://storage.googleapis.com/storage/v1/b?project={}: You already own this bucket. Please select another name.".format(
                    self.project
                )
            )
        else:
            self.backend.buckets[bucket.name] = bucket
        return bucket

    def download_blob_to_file(self, blob_or_uri, file_obj, start=None, end=None):
        raise NotImplementedError

    def list_blobs(
        self,
        bucket_or_name,
        max_results=None,
        page_token=None,
        prefix=None,
        delimiter=None,
        versions=None,
        projection="noAcl",
        fields=None,
    ):
        raise NotImplementedError

    def list_buckets(
        self,
        max_results=None,
        page_token=None,
        prefix=None,
        projection="noAcl",
        fields=None,
        project=None,
    ):
        if project is None:
            project = self.project

        if project is None:
            raise ValueError("Client project not set: pass an explicit project.")

        if isinstance(max_results, int):
            buckets = list(self.backend.buckets.values())[:max_results]
        else:
            buckets = list(self.backend.buckets.values())

        if isinstance(prefix, str):
            buckets = [bucket for bucket in buckets if bucket.name.startswith(prefix)]

        path = "/foo"
        page_response = {"items": buckets}
        api_request = mock.Mock(return_value=page_response)
        extra_params = {"key": "val"}

        return page_iterator.HTTPIterator(
            mock.sentinel.client,
            api_request,
            path=path,
            item_to_value=page_iterator._item_to_value_identity,
            max_results=max_results,
            page_token=mock.sentinel.token,
            extra_params=extra_params,
        )

    def create_hmac_key(
        self, service_account_email, project_id=None, user_project=None
    ):
        raise NotImplementedError

    def list_hmac_keys(
        self,
        max_results=None,
        service_account_email=None,
        show_deleted_keys=None,
        project_id=None,
        user_project=None,
    ):
        raise NotImplementedError

    def get_hmac_key_metadata(self, access_id, project_id=None, user_project=None):
        raise NotImplementedError


def _item_to_bucket(iterator, item):
    raise NotImplementedError


def _item_to_hmac_key_metadata(iterator, item):
    raise NotImplementedError
