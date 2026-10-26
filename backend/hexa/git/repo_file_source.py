from collections.abc import Iterator, Mapping
from functools import cached_property

from hexa.core.text_files import PathPattern, decode_text

from .client import GitClient
from .enums import FileEncoding
from .exceptions import GitFileTooLarge
from .forgejo import MAX_INLINE_BLOB_SIZE


class GitRepoFileSource(Mapping):
    """The files of a repository at `ref`: paths from one tree request, contents on lookup.

    Listing paths, as a glob does, never downloads content. A lookup fetches that one
    file, unless `search_glob` (the files a search is about to read) matches several in
    the tree: the first lookup then loads them all at once through `get_repository_files`
    (one archive download for a small repository). Contents are kept for the lifetime of
    the source. Binary and too large files map to None.
    """

    def __init__(
        self,
        client: GitClient,
        repo_name: str,
        ref: str,
        org_slug: str | None = None,
        search_glob: str | None = None,
    ):
        self._client = client
        self._repo_name = repo_name
        self._ref = ref
        self._org_slug = org_slug
        self._search_glob = search_glob
        self._contents: dict[str, str | None] = {}

    def __getitem__(self, path: str) -> str | None:
        if path not in self._sizes:
            raise KeyError(path)
        if path not in self._contents:
            if self._loads_all:
                self._contents = self._load_all()
            else:
                self._contents[path] = self._fetch(path)
        return self._contents[path]

    def __contains__(self, path: object) -> bool:
        return path in self._sizes

    def __iter__(self) -> Iterator[str]:
        return iter(self._sizes)

    def __len__(self) -> int:
        return len(self._sizes)

    @cached_property
    def _tree(self) -> list[dict]:
        return self._client.get_files_tree(
            self._repo_name, self._ref, org_slug=self._org_slug
        )

    @cached_property
    def _sizes(self) -> dict[str, int]:
        return {
            e["path"]: e.get("size") or 0 for e in self._tree if e.get("type") == "blob"
        }

    @cached_property
    def _loads_all(self) -> bool:
        """True if the search glob matches in more than 1 file"""
        if self._search_glob is None:
            return False
        pattern = PathPattern(self._search_glob)
        return sum(1 for p in self._sizes if pattern.matches(p)) > 1

    def _fetch(self, path: str) -> str | None:
        # Same ceiling as get_repository_files, so both ways of loading agree.
        if self._sizes[path] >= MAX_INLINE_BLOB_SIZE:
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
            for entry in self._client.get_repository_files(
                self._repo_name, self._ref, org_slug=self._org_slug, tree=self._tree
            )
            if entry["type"] == "file"
        }
