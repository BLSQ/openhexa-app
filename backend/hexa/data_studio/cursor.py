"""The opaque cursor of keyset pagination: the last row's sort key, signed.

Tied to the statement text and the ordering it was built for, so a changed sort or
query is refused rather than answered with the wrong rows. The statement text
rather than the saved query's identity: once templating lands, different
parameters render different text and invalidate the cursor for free. The page
size is deliberately left out; changing it mid-walk is harmless for a keyset.
"""

import datetime
import hashlib
import json

from django.core import signing

from hexa.databases.query_text import OrderBy
from hexa.databases.utils import ResultJSONEncoder

_SALT = "hexa.data_studio.cursor"


class InvalidCursor(Exception):
    """A cursor that is forged, stale, or built for another query or ordering."""


def _fingerprint(sql_text: str, order_by: list[OrderBy]) -> str:
    digest = hashlib.sha256(sql_text.encode())
    for key in order_by:
        digest.update(f"\0{key.column}\0{key.direction.value}".encode())
    return digest.hexdigest()[:16]


def _literal(value):
    """``value`` as a literal PostgreSQL coerces back to the column type.

    Built from the row as fetched rather than from its JSON form in the result:
    ``DjangoJSONEncoder`` keeps only milliseconds of a timestamp, and a cursor cut
    from that points between rows, repeating or skipping the ones in the gap.
    json/jsonb values travel as text because psycopg2 adapts neither dict nor list.
    """
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    if isinstance(value, (bool, int, float, str)):
        return value
    return ResultJSONEncoder().default(value)


def encode_cursor(sql_text: str, order_by: list[OrderBy], row: dict) -> str | None:
    """The cursor pointing at ``row``; ``None`` when its sort key holds a NULL.

    The same cursor serves both directions: passed as ``after`` it yields the
    rows past ``row``, as ``before`` the rows ahead of it. ``row`` is the row as
    psycopg2 fetched it, not its JSON form in the result. A keyset comparison
    never matches NULL, so such a row cannot be paged from. Reporting that as a
    missing cursor rather than an error keeps an offset-mode caller, who never
    uses the cursor, from being refused for it.
    """
    values = [row.get(key.column) for key in order_by]
    if any(value is None for value in values):
        return None
    payload = {
        "v": [_literal(v) for v in values],
        "f": _fingerprint(sql_text, order_by),
    }
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
