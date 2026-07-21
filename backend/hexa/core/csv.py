import csv
import datetime
import json
import re
import typing
from decimal import Decimal
from tempfile import SpooledTemporaryFile

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
    instead of buffering it, which is what lets ``iter_csv`` emit lines one by
    one.
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
    server-side database cursor. This is the single serialisation point used by
    :func:`buffered_csv_response`.
    """
    writer = csv.writer(Echo())
    if with_bom:
        yield UTF8_BOM
    yield writer.writerow([stringify_cell(cell) for cell in header])
    for row in rows:
        yield writer.writerow([stringify_cell(cell) for cell in row])


def buffered_csv_response(
    *,
    header: typing.Sequence[typing.Any],
    rows: typing.Iterable[typing.Sequence[typing.Any]],
    filename: str,
    with_bom: bool = True,
) -> FileResponse:
    """Materialise the whole CSV, then return it as a downloadable attachment.

    Every row is written to a spooled temp file *before* the response is
    returned, so a failure while producing rows (an invalid query, a statement
    timeout mid-scan, a dropped DB connection) raises from here — before any byte
    has reached the client — letting the caller return a clean error status
    instead of a silently truncated download. Peak memory stays bounded: the
    buffer spills to disk past ``_CSV_SPOOL_MAX_MEMORY``.

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


def streaming_csv_response(
    *,
    header: typing.Sequence[typing.Any],
    rows: typing.Iterable[typing.Sequence[typing.Any]],
    filename: str,
    with_bom: bool = True,
    on_finish: typing.Optional[typing.Callable[[], None]] = None,
) -> StreamingHttpResponse:
    """Stream ``header`` + ``rows`` as a downloadable CSV, one line at a time.

    Unlike :func:`buffered_csv_response`, bytes flow to the client as soon as they
    are produced instead of after the whole result is materialised, so a large
    export starts downloading immediately and is not exposed to a proxy
    idle-timeout while nothing is sent. Peak memory stays bounded to whatever the
    ``rows`` iterable holds at a time (e.g. one server-side cursor batch).

    The trade-off: the status line and headers are committed with the first
    chunk, so a failure raised by ``rows`` *after* that point cannot become an
    error status — the download simply ends truncated. A caller that must react
    to (or record) such a mid-stream failure has to observe ``rows`` itself, which
    is where the exception surfaces.

    ``on_finish``, if given, is called exactly once when the stream ends — normal
    completion, an error raised mid-stream, or the client disconnecting — tying
    resource release (a DB connection, an admission-control slot) to the stream's
    lifetime rather than to the view returning. It runs inside the generator that
    Django closes together with the response, so it fires even on an early client
    disconnect.
    """
    _require_csv_filename(filename)

    def byte_chunks() -> typing.Iterator[bytes]:
        try:
            for chunk in iter_csv(header=header, rows=rows, with_bom=with_bom):
                yield chunk.encode("utf-8")
        finally:
            if on_finish is not None:
                on_finish()

    response = StreamingHttpResponse(
        byte_chunks(), content_type="text/csv; charset=utf-8"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
