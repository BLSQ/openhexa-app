from collections.abc import Iterator
from functools import cached_property

from hexa.core.text_files import FileSource, decode_text

from .client import GitClient
from .enums import FileEncoding, TreeEntryType
from .exceptions import GitFileTooLarge
from .forgejo import MAX_INLINE_BLOB_SIZE


class GitRepoFileSource(FileSource):
    """The files of a repository at `ref`: paths from one tree request, contents on lookup.

    Listing paths, as a glob does, never downloads content. A lookup fetches that one
    file, unless a search prefetches several: they then load all at once through
    `get_repository_files_from_tree` (one archive download for a small repository). Contents are
    kept for the lifetime of the source. Binary and too large files map to None.
    """

    def __init__(
        self,
        client: GitClient,
        repo_name: str,
        ref: str,
        org_slug: str | None = None,
    ):
        self._client = client
        self._repo_name = repo_name
        self._ref = ref
        self._org_slug = org_slug
        self._contents: dict[str, str | None] = {}

    def __getitem__(self, path: str) -> str | None:
        if path not in self._file_sizes:
            raise KeyError(path)
        if path not in self._contents:
            self._contents[path] = self._fetch(path)
        return self._contents[path]

    def __contains__(self, path: object) -> bool:
        return path in self._file_sizes

    def __iter__(self) -> Iterator[str]:
        return iter(self._file_sizes)

    def __len__(self) -> int:
        return len(self._file_sizes)

    def prefetch(self, paths: list[str]) -> None:
        missing = (p not in self._contents for p in paths)
        # The second any() resumes where the first stopped, so both hold only if two paths are missing.
        several_missing = any(missing) and any(missing)
        if several_missing:
            self._contents = self._load_all()

    @cached_property
    def _tree(self) -> list[dict]:
        return self._client.get_files_tree(
            self._repo_name, self._ref, org_slug=self._org_slug
        )

    @cached_property
    def _file_sizes(self) -> dict[str, int]:
        return {
            e["path"]: e.get("size") or 0
            for e in self._tree
            if e.get("type") == TreeEntryType.BLOB
        }

    def _fetch(self, path: str) -> str | None:
        # Same ceiling as get_repository_files_from_tree, so both ways of loading agree.
        if self._file_sizes[path] >= MAX_INLINE_BLOB_SIZE:
            return None
        try:
            raw = self._client.get_file(
                self._repo_name, path, self._ref, org_slug=self._org_slug
            )
        except GitFileTooLarge:
            return None
        return decode_text(raw)

    def _load_all(self) -> dict[str, str | None]:
        return {
            entry["path"]: entry["content"]
            if entry["encoding"] == FileEncoding.TEXT
            else None
            for entry in self._client.get_repository_files_from_tree(
                self._repo_name, self._tree, self._ref, org_slug=self._org_slug
            )
            if entry["type"] == "file"
        }
