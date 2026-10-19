from collections.abc import Iterator, Mapping
from functools import cached_property

from hexa.core.text_files import TextFiles
from hexa.git.client import GitClient
from hexa.git.exceptions import GitFileNotFound, GitFileTooLarge

# Same ceiling as reading a text file from a workspace bucket.
MAX_TEXT_FILE_SIZE = 1024 * 1024


def decode_text(raw: bytes) -> str | None:
    """The UTF-8 text of a blob, or None for binary content."""
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


class GitFiles(Mapping):
    """The files of a git ref by path, fetched on first access.

    Listing costs one tree request; each content is one request, made only when read.
    Binary and oversized files map to None.
    """

    def __init__(self, client: GitClient, repository: str, ref: str, org_slug: str):
        self._client = client
        self._repository = repository
        self._ref = ref
        self._org_slug = org_slug
        self._contents: dict[str, str | None] = {}

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
        tree = self._client.get_files_tree(
            self._repository, self._ref, org_slug=self._org_slug
        )
        return {
            entry["path"]: entry.get("size") or 0
            for entry in tree
            if entry.get("type") == "blob"
        }

    def _fetch(self, path: str) -> str | None:
        if self._sizes[path] > MAX_TEXT_FILE_SIZE:
            return None
        try:
            raw = self._client.get_file(
                self._repository, path, self._ref, org_slug=self._org_slug
            )
        except GitFileTooLarge:
            return None
        except GitFileNotFound:
            raise KeyError(path)
        return decode_text(raw)


class GitTextFilesMixin:
    """Reads a repository's text files.

    Kept apart from GitRepoMixin so models opt into file reading on its own. The host
    provides `client`, `repository` and `git_org`, as GitRepoMixin does.
    """

    def get_text_files(self, ref: str = "main") -> TextFiles:
        return TextFiles(GitFiles(self.client, self.repository, ref, self.git_org.slug))
