from collections.abc import Iterable, Iterator, Mapping

from .source import FileSource


class Overlay(FileSource):
    """A base mapping seen through changes and deletions, without copying or loading it."""

    def __init__(
        self,
        base: FileSource,
        changes: Mapping[str, str],
        deleted: Iterable[str] = (),
    ):
        self._base = base
        self._changes = changes
        self._deleted = set(deleted) - set(changes)

    def __getitem__(self, path: str) -> str | None:
        if path in self._changes:
            return self._changes[path]
        if path in self._deleted:
            raise KeyError(path)
        return self._base[path]

    def __contains__(self, path: object) -> bool:
        return path in self._changes or (
            path not in self._deleted and path in self._base
        )

    def __iter__(self) -> Iterator[str]:
        yield from self._changes
        yield from (
            p for p in self._base if p not in self._changes and p not in self._deleted
        )

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def prefetch(self, paths: list[str]) -> None:
        self._base.prefetch([p for p in paths if p not in self._changes])
