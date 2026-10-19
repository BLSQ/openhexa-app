from collections.abc import Iterator
from functools import cached_property

from hexa.core.text_files import MAX_TEXT_FILE_SIZE, FileSource, decode_text

from .backends.base import Storage
from .backends.exceptions import NotFound

# A bucket can hold far more files than an agent could use; listing stops here.
MAX_LISTED_FILES = 5000
# Large pages keep the request count down: backends re-iterate from the start per page.
_LIST_PAGE_SIZE = 1000


class BucketFileSource(FileSource):
    """The files of a workspace bucket under `prefix`, downloaded on first access.

    Listing walks the directories, one request per directory and page, up to
    MAX_LISTED_FILES (`truncated` tells when it stopped there). Each content is a full
    download, made only when read: searching a bucket is far costlier than a repository.
    Hidden, binary and oversized files are skipped or map to None, as in `list_files`.
    """

    def __init__(self, storage: Storage, bucket_name: str, prefix: str = ""):
        self._storage = storage
        self._bucket_name = bucket_name
        self._prefix = prefix
        self._contents: dict[str, str | None] = {}
        self.truncated = False

    def __getitem__(self, path: str) -> str | None:
        if path not in self._sizes:
            raise KeyError(path)
        if path not in self._contents:
            self._contents[path] = self._fetch(path)
        return self._contents[path]

    def __contains__(self, path: object) -> bool:
        return path in self._sizes

    def __iter__(self) -> Iterator[str]:
        return iter(self._sizes)

    def __len__(self) -> int:
        return len(self._sizes)

    @cached_property
    def _sizes(self) -> dict[str, int]:
        sizes: dict[str, int] = {}
        directories = [self._prefix]
        while directories:
            prefix = directories.pop()
            for obj in self._list(prefix):
                # Backends disagree on key types and trailing slashes for directories.
                key = str(obj.key).rstrip("/")
                if obj.type == "directory":
                    # A folder placeholder listed under itself would loop forever.
                    if f"{key}/" != prefix:
                        directories.append(f"{key}/")
                    continue
                if len(sizes) == MAX_LISTED_FILES:
                    self.truncated = True
                    return sizes
                sizes[key] = obj.size or 0
        return sizes

    def _list(self, prefix: str) -> Iterator:
        page = 1
        while True:
            result = self._storage.list_bucket_objects(
                self._bucket_name, prefix=prefix, page=page, per_page=_LIST_PAGE_SIZE
            )
            yield from result.items
            if not result.has_next_page:
                return
            page += 1

    def _fetch(self, path: str) -> str | None:
        if self._sizes[path] > MAX_TEXT_FILE_SIZE:
            return None
        try:
            raw = self._storage.read_object(self._bucket_name, path)
        except NotFound:
            raise KeyError(path)
        return decode_text(raw)
