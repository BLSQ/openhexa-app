import csv
import datetime
import json
import math
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


def _format_float_like_js(value: float) -> str:
    """Format a float exactly as JavaScript's ``Number.prototype.toString`` does.

    A ``float8``/``float4`` column crosses the interactive path as a JSON number and
    is rendered client-side with ``String(x)``; Python's ``repr`` diverges from that at
    the exponent thresholds (``1e16`` -> ``"1e+16"`` vs ``"10000000000000000"``, ``1e-7``
    -> ``"1e-07"`` vs ``"1e-7"``) and for non-finite values. Following ECMA-262's
    algorithm keeps float columns byte-identical across both export paths.
    """
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    if value == 0:
        return "0"  # JS renders both +0 and -0 as "0"
    sign = "-" if value < 0 else ""
    magnitude = -value if value < 0 else value

    # Decompose repr's shortest round-tripping digits into ECMA's bare digit string
    # ``s`` and decimal-point position ``n`` (value == int(s) * 10 ** (n - len(s))).
    rep = repr(magnitude)
    if "e" in rep:
        mantissa, _, exp_text = rep.partition("e")
        exponent = int(exp_text)
    else:
        mantissa, exponent = rep, 0
    int_part, _, frac_part = mantissa.partition(".")
    combined = int_part + frac_part
    point = exponent - len(frac_part)
    stripped = combined.lstrip("0")
    s = stripped.rstrip("0")
    point += len(stripped) - len(s)  # trailing zeros fold back into the exponent
    k = len(s)
    n = point + k

    if k <= n <= 21:
        return sign + s + "0" * (n - k)
    if 0 < n <= 21:
        return sign + s[:n] + "." + s[n:]
    if -6 < n <= 0:
        return sign + "0." + "0" * -n + s
    exp = n - 1
    mant = s if k == 1 else s[0] + "." + s[1:]
    return sign + mant + "e" + ("+" if exp >= 0 else "-") + str(abs(exp))


def stringify_cell(value: typing.Any) -> str:
    """Render a single value as a CSV-safe string.

    Numbers pass through untouched; free text that a spreadsheet could read as a
    formula is prefixed with a single quote to neutralise CSV injection.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return _format_float_like_js(value)
    if isinstance(value, (int, Decimal)):
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "\\x" + bytes(value).hex()
    if isinstance(value, (dict, list)):
        # Compact separators (no spaces) and ensure_ascii=False so this matches
        # the frontend's JSON.stringify byte-for-byte: JSON.stringify emits
        # non-ASCII literally, whereas json.dumps escapes it (\uXXXX) by default,
        # which would diverge for e.g. accented text in a JSONB column. See the
        # frontend buildCsv and its cross-path parity test.
        return json.dumps(
            value, default=str, separators=(",", ":"), ensure_ascii=False
        )
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


def _csv_line(writer: typing.Any, cells: typing.Sequence[typing.Any]) -> str:
    """Serialise one record to a CSV line.

    The single place a cell becomes CSV text: used by
    :func:`async_streaming_csv_response` and pinned directly by the shared
    cell-serialisation contract test, so the client and server export paths
    cannot diverge.
    """
    return writer.writerow([stringify_cell(cell) for cell in cells])


class _CleanupStreamingHttpResponse(StreamingHttpResponse):
    """A streaming response that runs a callback when Django closes it.

    Django calls ``close()`` on both normal completion and a client disconnect
    (its ASGI handler suppresses the disconnect ``CancelledError`` and still
    closes the response), which is the only deterministic hook for freeing
    resources when the client goes away mid-stream — an async generator's own
    ``finally`` waits on garbage collection in that case. See
    :func:`async_streaming_csv_response`.
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

    Returns an *async* streaming response, which is what actually streams under an
    ASGI worker: a sync generator would instead be drained into memory in one go
    (``StreamingHttpResponse.__aiter__`` falls back to ``sync_to_async(list)``),
    defeating the point. ``row_batches`` is therefore an async iterator whose items
    are batches of rows (e.g. one server-side cursor batch), so peak memory stays
    bounded to a single batch however large the result set is. The caller is
    responsible for doing any blocking work (a DB fetch) off the event loop before
    yielding a batch — see ``hexa.databases.views``.

    The trade-off: the status line and headers are committed with the first
    chunk, so a failure raised by ``row_batches`` *after* that point cannot become
    an error status — the download simply ends truncated. A caller that must react
    to (or record) such a mid-stream failure has to observe ``row_batches`` itself,
    which is where the exception surfaces (see
    ``hexa.databases.views.download_query_csv`` for how likely that is in practice
    and how it is handled).

    ``on_finish``, if given, is run exactly once when the stream ends, tying
    resource release (a DB connection, an admission-control slot) to the stream's
    lifetime rather than to the view returning. It has to fire on three different
    endings, which reach us by two different routes:

    * normal completion and a mid-stream error both unwind the byte generator, so
      its ``finally`` runs ``on_finish``;
    * a client disconnect does *not* promptly run that ``finally`` — Django closes
      only its own outer wrapper, leaving our async generator (and its ``finally``)
      to garbage collection — but Django *does* call ``response.close()`` on
      disconnect, so :class:`_CleanupStreamingHttpResponse` runs ``on_finish`` from
      there.

    A once-guard makes the overlap (normal completion takes both routes) safe, so
    ``on_finish`` still fires exactly once. Because it may run from
    ``response.close()``, the caller must make ``on_finish`` do everything a
    disconnect needs — e.g. close the DB cursor/connection, not only release a slot
    — since the ``row_batches`` generator's own ``finally`` is subject to the same
    GC delay.
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
