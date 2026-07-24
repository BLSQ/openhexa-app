import csv
import datetime
import json
import re
import threading
import typing
from contextlib import aclosing
from decimal import Decimal

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

    Passed to ``csv.writer`` so each ``writerow`` returns its formatted line
    (see :func:`_csv_line`) instead of writing it to a buffer, which is what lets
    the response stream lines one at a time.
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
        # str() gives the shortest round-tripping form; for a float that is the
        # same text Postgres itself prints for the value (e.g. 1e+16, 1e-07),
        # so the export stays faithful to the source and needs no custom logic.
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "\\x" + bytes(value).hex()
    if isinstance(value, (dict, list)):
        # json/jsonb columns arrive already parsed. Compact separators drop the
        # cosmetic whitespace; ensure_ascii=False keeps non-ASCII text literal
        # (é stays é) instead of \uXXXX-escaping it, so accented text survives.
        return json.dumps(value, default=str, separators=(",", ":"), ensure_ascii=False)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()

    text = str(value)
    # A text column may hold a value a spreadsheet would read as a formula; guard
    # it. A pure numeric literal is inert, so leave it intact rather than quoting.
    if not _NUMERIC_LITERAL.match(text) and _FORMULA_PREFIX.match(text):
        return "'" + text
    return text


def _require_csv_filename(filename: str) -> None:
    if not filename.endswith(".csv"):
        raise ValueError(f"Invalid filename {filename!r} - should end with .csv")


def _csv_line(writer: typing.Any, cells: typing.Sequence[typing.Any]) -> str:
    """Serialise one record to a CSV line.

    The single place a cell becomes CSV text: used by
    :func:`async_streaming_csv_response` and pinned by the cell-serialisation
    tests (see ``hexa.core.tests.test_csv``).
    """
    return writer.writerow([stringify_cell(cell) for cell in cells])


class _CleanupStreamingHttpResponse(StreamingHttpResponse):
    """A streaming response that runs a callback when Django closes it.

    Django calls ``close()`` on a client disconnect — where an async generator's own
    ``finally`` would wait on GC — so it is the deterministic hook for freeing
    resources when the client goes away mid-stream. See
    :func:`async_streaming_csv_response` and the app README.
    """

    def __init__(self, *args, on_close: typing.Callable[[], None], **kwargs) -> None:
        self._on_close = on_close
        super().__init__(*args, **kwargs)

    def close(self) -> None:
        try:
            self._on_close()
        finally:
            super().close()


def async_streaming_csv_response(
    *,
    header: typing.Sequence[typing.Any],
    row_batches: typing.AsyncIterator[typing.Iterable[typing.Sequence[typing.Any]]],
    filename: str,
    with_bom: bool = True,
    on_finish: typing.Optional[typing.Callable[[], None]] = None,
) -> StreamingHttpResponse:
    """Stream ``header`` + ``row_batches`` as a downloadable CSV, batch by batch.

    ``row_batches`` must be an *async* iterator of row batches: under an ASGI worker a
    sync generator would be drained into memory in one go, defeating the streaming. The
    caller does its blocking work (a DB fetch) off the event loop before yielding each
    batch, so peak memory stays bounded to one batch — see ``hexa.databases.views``.

    ``on_finish``, if given, fires exactly once when the stream ends: on normal
    completion and a mid-stream error (via the byte generator's ``finally``) and on a
    client disconnect (via :class:`_CleanupStreamingHttpResponse`, since the generator's
    ``finally`` waits on GC then); a once-guard makes the overlap safe. Because it may run
    from ``response.close()``, ``on_finish`` must do everything a disconnect needs — close
    the DB cursor/connection, not only release a slot.

    The app README covers the streaming rationale and the mid-stream-truncation trade-off
    (headers commit with the first chunk, so a later failure can't change the 200 status).
    """
    _require_csv_filename(filename)
    writer = csv.writer(Echo())

    finish_lock = threading.Lock()
    finished = False

    def finish_once() -> None:
        nonlocal finished
        if on_finish is None:
            return
        with finish_lock:
            if finished:
                return
            finished = True
        on_finish()

    async def byte_chunks() -> typing.AsyncIterator[bytes]:
        try:
            if with_bom:
                yield UTF8_BOM.encode("utf-8")
            yield _csv_line(writer, header).encode("utf-8")
            async with aclosing(row_batches) as batches:
                async for batch in batches:
                    yield "".join(_csv_line(writer, row) for row in batch).encode(
                        "utf-8"
                    )
        finally:
            finish_once()

    response = _CleanupStreamingHttpResponse(
        byte_chunks(),
        content_type="text/csv; charset=utf-8",
        on_close=finish_once,
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
