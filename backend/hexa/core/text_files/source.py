from collections.abc import Mapping

MAX_TEXT_FILE_SIZE = 1024 * 1024


class FileSource(Mapping[str, str | None]):
    """What TextFiles reads: every path mapped to its text, or None if not text."""

    def prefetch(self, paths: list[str]) -> None:
        """Hint that `paths` are about to be read; sources that can batch downloads do."""


class MemoryFileSource(dict, FileSource):
    """Files held in memory, e.g. in tests."""


def decode_text(raw: bytes) -> str | None:
    """The UTF-8 text of a blob, or None for binary content."""
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
