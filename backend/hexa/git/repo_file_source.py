from collections.abc import Iterator, Mapping
from functools import cached_property

from .client import GitClient
from .enums import FileEncoding


class GitRepoFileSource(Mapping):
    """The files of a repository at `ref`: paths from one tree request, contents on first
    access.

    Listing paths, as a glob does, never downloads content. The first content lookup
    loads every file at once through `get_repository_files` (one archive download for a
    small repository) and keeps them, so a grep or several reads cost one download.
    Binary and too large files map to None.
    """

    def __init__(
        self, client: GitClient, repo_name: str, ref: str, org_slug: str | None = None
    ):
        self._client = client
        self._repo_name = repo_name
        self._ref = ref
        self._org_slug = org_slug

    def __getitem__(self, path: str) -> str | None:
        if path not in self._paths:
            raise KeyError(path)
        return self._contents.get(path)

    def __contains__(self, path: object) -> bool:
        return path in self._paths

    def __iter__(self) -> Iterator[str]:
        return iter(self._paths)

    def __len__(self) -> int:
        return len(self._paths)

    @cached_property
    def _tree(self) -> list[dict]:
        return self._client.get_files_tree(
            self._repo_name, self._ref, org_slug=self._org_slug
        )

    @cached_property
    def _paths(self) -> dict[str, None]:
        return dict.fromkeys(e["path"] for e in self._tree if e.get("type") == "blob")

    @cached_property
    def _contents(self) -> dict[str, str | None]:
        return {
            entry["path"]: entry["content"]
            if entry["encoding"] == FileEncoding.TEXT
            else None
            for entry in self._client.get_repository_files(
                self._repo_name, self._ref, org_slug=self._org_slug, tree=self._tree
            )
            if entry["type"] == "file"
        }
