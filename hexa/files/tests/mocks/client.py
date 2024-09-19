from google.api_core import page_iterator
from google.cloud.exceptions import Conflict, NotFound

from .bucket import MockBucket


class MockHTTPIterator:
    def __init__(self, items, page_size, max_results=None):
        self.items = items
        self._page_size = page_size
        self.num_results = 0
        self.page_number = 0
        self.max_results = max_results
        self._started = False
        self.__active_iterator = None

    def __iter__(self):
        """Iterator for each item returned.

        Returns
        -------
            types.GeneratorType[Any]: A generator of items from the API.

        Raises
        ------
            ValueError: If the iterator has already been started.
        """
        if self._started:
            raise ValueError("Iterator has already started", self)
        self._started = True
        return self._items_iter()

    def __next__(self):
        if self.__active_iterator is None:
            self.__active_iterator = iter(self)
        return next(self.__active_iterator)

    def _items_iter(self):
        """Iterator for each item returned."""
        for page in self._page_iter(increment=False):
            for item in page:
                self.num_results += 1
                yield item

    @property
    def prefixes(self):
        return set([item.name for item in self.items if item.name.endswith("/")])

    @property
    def pages(self):
        if self._started:
            raise ValueError("Iterator has already started", self)
        self._started = True
        return self._page_iter(increment=True)

    def _page_iter(self, increment):
        """Generator of pages of API responses.

        Args:
            increment (bool): Flag indicating if the total number of results
                should be incremented on each page. This is useful since a page
                iterator will want to increment by results per page while an
                items iterator will want to increment per item.

        Yields
        ------
            Page: each page of items from the API.
        """
        page = self._next_page()
        while page is not None:
            self.page_number += 1
            if increment:
                self.num_results += page.num_items
            yield page
            page = self._next_page()

    def _next_page(self):
        """Get the next page in the iterator.

        Returns
        -------
            Optional[Page]: The next page in the iterator or :data:`None` if
                there are no pages left.
        """
        if self._has_next_page():
            page = page_iterator.Page(
                self,
                self.items[self.num_results : self.num_results + self._page_size],
                lambda _, item: item,
            )
            return page
        else:
            return None

    def _has_next_page(self):
        """Determines whether or not there are more pages with results.

        Returns
        -------
            bool: Whether the iterator has more pages.
        """
        if self.page_number == 0:
            return True

        if self.max_results is not None:
            if self.num_results >= self.max_results:
                return False

        return self.num_results < len(self.items)


class MockClient:
    def __init__(
        self,
        credentials=None,
        _http=None,
        client_info=None,
        client_options=None,
        *args,
        **kwargs,
    ):
        self.buckets = {}
        self.credentials = credentials
        self._http = _http
        self.client_info = client_info
        self.client_options = client_options

    def _push_batch(self, batch):
        raise NotImplementedError

    def _pop_batch(self):
        raise NotImplementedError

    def _bucket_arg_to_bucket(self, bucket_or_name):
        if isinstance(bucket_or_name, MockBucket):
            bucket = bucket_or_name
        else:
            bucket = self.buckets.get(bucket_or_name)
        return bucket

    @property
    def current_batch(self):
        raise NotImplementedError

    def get_service_account_email(self, project=None):
        raise NotImplementedError

    def bucket(self, bucket_name, user_project=None):
        return MockBucket(client=self, name=bucket_name, user_project=user_project)

    def delete_bucket(self, bucket_name):
        if bucket_name in self.buckets:
            del self.buckets[bucket_name]
        else:
            raise NotFound(
                f"404 DELETE https://storage.googleapis.com/storage/v1/b/{bucket_name}"
            )

    def batch(self):
        raise NotImplementedError

    def get_bucket(self, bucket_or_name):
        bucket = self._bucket_arg_to_bucket(bucket_or_name)

        if bucket is None or bucket.name not in self.buckets.keys():
            raise NotFound(
                f"404 GET https://storage.googleapis.com/storage/v1/b/{bucket_or_name}?projection=noAcl"
            )
        else:
            return self.buckets[bucket.name]

    def lookup_bucket(self, bucket_name):
        try:
            return self.get_bucket(bucket_name)
        except NotFound:
            return None

    def create_bucket(
        self, bucket_or_name=None, Bucket=None, labels=None, *args, **kwargs
    ):
        bucket_or_name = bucket_or_name or Bucket
        bucket = self._bucket_arg_to_bucket(bucket_or_name)
        if bucket is None:
            bucket = MockBucket(
                client=self,
                name=bucket_or_name,
                labels=labels,
            )

        if bucket.name in self.buckets.keys():
            raise Conflict(
                "409 POST https://storage.googleapis.com/storage/v1/b?project={}: You already own this bucket. Please select another name.".format(
                    self.project
                )
            )
        else:
            self.buckets[bucket.name] = bucket
        return bucket

    def download_blob_to_file(self, blob_or_uri, file_obj, start=None, end=None):
        raise NotImplementedError

    def list_blobs(
        self, bucket_or_name, max_results=None, prefix=None, page_size=None, **kwargs
    ):
        bucket = self._bucket_arg_to_bucket(bucket_or_name)
        if bucket is None:
            raise NotFound(
                f"404 GET https://storage.googleapis.com/storage/v1/b/{bucket_or_name}?projection=noAcl"
            )
        if isinstance(max_results, int):
            blobs = bucket._blobs[:max_results]
        else:
            blobs = bucket._blobs[: len(bucket._blobs)]
        if isinstance(prefix, str):
            blobs = [
                blob
                for blob in blobs
                if blob.name.startswith(prefix) and blob.name != prefix
            ]

        # Only take the blobs at the prefix and not the blobs in "subdirectories"
        prefix_len = len(prefix or "")
        blobs = [
            blob
            for blob in blobs
            if blob.name[prefix_len:].find("/") < 0
            or blob.name[prefix_len:].find("/") == len(blob.name[prefix_len:]) - 1
        ]

        blobs.sort(key=lambda blob: blob.name)

        iterator = MockHTTPIterator(
            items=blobs,
            page_size=page_size,
            max_results=max_results,
        )

        return iterator

    def list_buckets(
        self,
        max_results=None,
        prefix=None,
        page_size=None,
        **kwargs,
    ):
        if isinstance(max_results, int):
            buckets = list(self.buckets.values())[:max_results]
        else:
            buckets = list(self.buckets.values())

        if isinstance(prefix, str):
            buckets = [bucket for bucket in buckets if bucket.name.startswith(prefix)]

        # The default page_size is set by the server
        page_size = page_size if page_size else 10

        return MockHTTPIterator(
            items=buckets, max_results=max_results, page_size=page_size
        )
