"""The opaque cursor of keyset pagination: the last row's sort key, signed.

Tied to the statement text and the ordering it was built for, so a changed sort or
query is refused rather than answered with the wrong rows. The statement text
rather than the saved query's identity: once templating lands, different
parameters render different text and invalidate the cursor for free. The page
size is deliberately left out; changing it mid-walk is harmless for a keyset.
"""

import hashlib

from django.core import signing

from hexa.databases.query_text import OrderBy

_SALT = "hexa.data_studio.cursor"


class InvalidCursor(Exception):
    """A cursor that is forged, stale, or built for another query or ordering."""


def _fingerprint(sql_text: str, order_by: list[OrderBy]) -> str:
    digest = hashlib.sha256(sql_text.encode())
    for key in order_by:
        digest.update(f"\0{key.column}\0{key.direction.value}".encode())
    return digest.hexdigest()[:16]


def encode_cursor(sql_text: str, order_by: list[OrderBy], last_row: dict) -> str | None:
    """The cursor pointing past ``last_row``; ``None`` when its sort key holds a NULL.

    A keyset comparison never matches NULL, so such a row cannot be paged from.
    Reporting that as a missing cursor rather than an error keeps an offset-mode
    caller, who never uses the cursor, from being refused for it.
    """
    values = [last_row.get(key.column) for key in order_by]
    if any(value is None for value in values):
        return None
    payload = {"v": values, "f": _fingerprint(sql_text, order_by)}
    return signing.dumps(payload, salt=_SALT, compress=True)


def decode_cursor(cursor: str, sql_text: str, order_by: list[OrderBy]) -> list:
    """The sort-key values a cursor points past, for the same query and ordering."""
    try:
        payload = signing.loads(cursor, salt=_SALT)
    except signing.BadSignature:
        raise InvalidCursor("The cursor is not valid.")
    if not isinstance(payload, dict) or payload.get("f") != _fingerprint(
        sql_text, order_by
    ):
        raise InvalidCursor("The cursor does not match this query and ordering.")
    values = payload.get("v")
    if not isinstance(values, list) or len(values) != len(order_by):
        raise InvalidCursor("The cursor does not match this ordering.")
    if any(value is None for value in values):
        raise InvalidCursor(
            "The cursor points at a row this ordering cannot page from."
        )
    return values
