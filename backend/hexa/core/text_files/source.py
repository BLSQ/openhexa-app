from collections.abc import Mapping

# Same ceiling as reading a text file from a workspace bucket.
MAX_TEXT_FILE_SIZE = 1024 * 1024


class FileSource(Mapping):
    """Files by path, as TextFiles reads them.

    Iterating lists every file, binary ones included. `source[path]` is the file's text,
    or None when it cannot be read as text (binary, too large); an unknown path raises
    KeyError. A lookup may cost a request or a download, so subclasses fetch lazily and
    cache, letting `glob` touch paths alone and `grep` stop early.
    """


def decode_text(raw: bytes) -> str | None:
    """The UTF-8 text of a blob, or None for binary content."""
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
