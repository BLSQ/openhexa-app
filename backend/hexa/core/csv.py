import csv
import datetime
import json
import re
import typing
from decimal import Decimal
from operator import attrgetter

from django.db.models import QuerySet
from django.http import StreamingHttpResponse

# Excel decodes a UTF-8 CSV as the local ANSI codepage unless it sees a BOM,
# which mangles accented characters. Prepend one so non-ASCII data survives.
UTF8_BOM = "\ufeff"

# A numeric literal as Postgres emits it: optional leading '-', digits, optional
# fraction, optional exponent. No leading '+' (Postgres never emits "+5"), so a
# '+'-prefixed value is genuine text, not a number.
_NUMERIC_LITERAL = re.compile(r"^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")

# Leading characters a spreadsheet interprets as the start of a formula.
_FORMULA_PREFIX = re.compile(r"^[=+\-@\t\r]")


class Echo:
    """A file-like object whose ``write`` returns the value written.

    Passed to ``csv.writer`` so each ``writerow`` yields its formatted line
    instead of buffering it, which is what lets ``stream_csv`` emit rows lazily.
    """

    def write(self, value: str) -> str:
        return value


def stringify_cell(value: typing.Any) -> str:
    """Render a single value as a CSV-safe string.

    Numbers pass through untouched; free text that a spreadsheet could read as a
    formula is prefixed with a single quote to neutralise CSV injection.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "\\x" + bytes(value).hex()
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()

    text = str(value)
    # NUMERIC/DECIMAL/bigint columns arrive as strings to preserve precision; a
    # pure numeric literal is inert in a spreadsheet, so leave it intact.
    if not _NUMERIC_LITERAL.match(text) and _FORMULA_PREFIX.match(text):
        return "'" + text
    return text


def stream_csv(
    *,
    header: typing.Sequence[typing.Any],
    rows: typing.Iterable[typing.Sequence[typing.Any]],
    filename: str,
    with_bom: bool = True,
) -> StreamingHttpResponse:
    """Stream ``rows`` as a CSV attachment without buffering them in memory.

    ``rows`` is consumed lazily, so the caller may pass a generator backed by a
    server-side database cursor to export arbitrarily large result sets.
    """
    if not filename.endswith(".csv"):
        raise ValueError(f"Invalid filename {filename!r} - should end with .csv")

    writer = csv.writer(Echo())

    def generate() -> typing.Iterator[str]:
        if with_bom:
            yield UTF8_BOM
        yield writer.writerow([stringify_cell(cell) for cell in header])
        for row in rows:
            yield writer.writerow([stringify_cell(cell) for cell in row])

    response = StreamingHttpResponse(generate(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _get_or_none(obj: typing.Any, field: str) -> typing.Any:
    try:
        return attrgetter(field)(obj)
    except (AttributeError, KeyError):
        return None


def render_queryset_to_csv(
    queryset: QuerySet, *, filename: str, field_names: typing.Sequence[str]
) -> StreamingHttpResponse:
    """Stream a queryset as CSV. Field names may use dots for nested access."""
    header = [name.replace(".", "_") for name in field_names]
    rows = ([_get_or_none(obj, field) for field in field_names] for obj in queryset)
    return stream_csv(header=header, rows=rows, filename=filename)
