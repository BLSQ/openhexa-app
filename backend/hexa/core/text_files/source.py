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
