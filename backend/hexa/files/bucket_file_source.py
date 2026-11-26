from collections.abc import Iterator
from functools import cached_property

from hexa.core.text_files import FileSource

from .backends.base import Storage

# A bucket can hold far more files than an agent could use; listing stops here.
MAX_LISTED_FILES = 5000
# Large pages keep the request count down: backends re-iterate from the start per page.
_LIST_PAGE_SIZE = 1000
# Guards against a backend that never stops reporting a next page.
_MAX_LIST_PAGES = 100


class BucketFileSource(FileSource):
    """The paths of a workspace bucket's files under `prefix`, listed on first access.

    Listing walks the directories, one request per directory and page, up to
    MAX_LISTED_FILES (`truncated` tells when it stopped there). Hidden files are
    skipped, as in `list_files`.

    Contents are never downloaded: every path maps to None, so the files can be globbed
    but not searched or read through this source. Buckets may hold sensitive data that
    must not be searchable by AI tools (HEXA-1917).
    """

    def __init__(self, storage: Storage, bucket_name: str, prefix: str = ""):
        self._storage = storage
        self._bucket_name = bucket_name
        self._prefix = prefix
        self.truncated = False

    def __getitem__(self, path: str) -> None:
        if path not in self._paths:
            raise KeyError(path)
        return None

    def __contains__(self, path: object) -> bool:
        return path in self._paths

    def __iter__(self) -> Iterator[str]:
        return iter(self._paths)

    def __len__(self) -> int:
        return len(self._paths)

    @cached_property
    def _paths(self) -> dict[str, None]:
        paths: dict[str, None] = {}
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
                if len(paths) == MAX_LISTED_FILES:
                    self.truncated = True
                    return paths
                paths[key] = None
        return paths

    def _list(self, prefix: str) -> Iterator:
        for page in range(1, _MAX_LIST_PAGES + 1):
            result = self._storage.list_bucket_objects(
                self._bucket_name, prefix=prefix, page=page, per_page=_LIST_PAGE_SIZE
            )
            yield from result.items
            if not result.has_next_page:
                return
        self.truncated = True
