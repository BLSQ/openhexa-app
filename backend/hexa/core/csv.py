import csv
import datetime
import json
import re
import typing
from decimal import Decimal
from operator import attrgetter
from tempfile import SpooledTemporaryFile

from django.db.models import QuerySet
from django.http import FileResponse, StreamingHttpResponse

# Buffer the CSV in memory up to this size before spilling to a temp file on
# disk. Bounds RAM per concurrent export while keeping small exports off disk.
_CSV_SPOOL_MAX_MEMORY = 8 * 1024 * 1024

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
        # Compact separators (no spaces) so this matches the frontend's
        # JSON.stringify byte-for-byte — see the frontend buildCsv and its
        # cross-path parity test.
        return json.dumps(value, default=str, separators=(",", ":"))
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()

    text = str(value)
    # NUMERIC/DECIMAL/bigint columns arrive as strings to preserve precision; a
    # pure numeric literal is inert in a spreadsheet, so leave it intact.
    if not _NUMERIC_LITERAL.match(text) and _FORMULA_PREFIX.match(text):
        return "'" + text
    return text


def _require_csv_filename(filename: str) -> None:
    if not filename.endswith(".csv"):
        raise ValueError(f"Invalid filename {filename!r} - should end with .csv")


def iter_csv(
    *,
    header: typing.Sequence[typing.Any],
    rows: typing.Iterable[typing.Sequence[typing.Any]],
    with_bom: bool = True,
) -> typing.Iterator[str]:
    """Yield the CSV text of ``header`` + ``rows``, one formatted line at a time.

    ``rows`` is consumed lazily, so the caller may pass a generator backed by a
    server-side database cursor. This is the single serialisation point shared by
    both :func:`stream_csv` and :func:`buffered_csv_response`.
    """
    writer = csv.writer(Echo())
    if with_bom:
        yield UTF8_BOM
    yield writer.writerow([stringify_cell(cell) for cell in header])
    for row in rows:
        yield writer.writerow([stringify_cell(cell) for cell in row])


def stream_csv(
    *,
    header: typing.Sequence[typing.Any],
    rows: typing.Iterable[typing.Sequence[typing.Any]],
    filename: str,
    with_bom: bool = True,
) -> StreamingHttpResponse:
    """Stream ``rows`` as a CSV attachment without buffering them in memory.

    ``rows`` is consumed lazily as the response is written. A failure while
    producing rows therefore surfaces *after* the ``200`` and some bytes are
    already on the wire, truncating the download silently — acceptable only when
    ``rows`` cannot realistically fail mid-iteration (e.g. a bounded ORM
    queryset). For an arbitrary user query, prefer :func:`buffered_csv_response`.
    """
    _require_csv_filename(filename)
    response = StreamingHttpResponse(
        iter_csv(header=header, rows=rows, with_bom=with_bom),
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def buffered_csv_response(
    *,
    header: typing.Sequence[typing.Any],
    rows: typing.Iterable[typing.Sequence[typing.Any]],
    filename: str,
    with_bom: bool = True,
) -> FileResponse:
    """Materialise the whole CSV, then return it as a downloadable attachment.

    Unlike :func:`stream_csv`, every row is written to a spooled temp file
    *before* the response is returned, so a failure while producing rows (an
    invalid query, a statement timeout mid-scan, a dropped DB connection) raises
    from here — before any byte has reached the client — letting the caller
    return a clean error status instead of a silently truncated download. Peak
    memory stays bounded: the buffer spills to disk past ``_CSV_SPOOL_MAX_MEMORY``.

    The trade-off is latency: the client sees nothing until the query has fully
    run and serialised. See ``hexa.databases.views.download_query_csv`` for the
    expected wait by result size.
    """
    _require_csv_filename(filename)
    spool = SpooledTemporaryFile(max_size=_CSV_SPOOL_MAX_MEMORY, mode="w+b")
    try:
        for chunk in iter_csv(header=header, rows=rows, with_bom=with_bom):
            spool.write(chunk.encode("utf-8"))
    except Exception:
        spool.close()
        raise
    spool.seek(0)
    # FileResponse sets Content-Length from the (seekable) spool, so the browser
    # gets a definite size and can itself detect a truncated transfer. It also
    # closes the spool — and thus removes the temp file — when the response ends.
    return FileResponse(
        spool,
        as_attachment=True,
        filename=filename,
        content_type="text/csv; charset=utf-8",
    )


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
