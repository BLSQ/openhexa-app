import csv
import datetime
from decimal import Decimal

from asgiref.sync import async_to_sync

from hexa.core.test import TestCase

from ..csv import (
    UTF8_BOM,
    Echo,
    _csv_line,
    async_streaming_csv_response,
)

# How a single cell must serialise, as (description, value, expected) — expected is
# the cell post-guard and post-quote. Float expectations follow Python's str(), the
# shortest round-tripping form and the same text Postgres prints for a float8
# (e.g. 1e+16, 1e-07).
CSV_CELL_VECTORS = [
    ("null becomes an empty cell", None, ""),
    ("boolean true is lowercased", True, "true"),
    ("boolean false is lowercased", False, "false"),
    ("plain text passes through", "hello", "hello"),
    ("ordinary text that merely looks number-ish is not guarded", "N/A", "N/A"),
    ("integer number", 42, "42"),
    ("negative integer number is not an injection risk", -5, "-5"),
    ("decimal number", 1.5, "1.5"),
    ("negative float keeps its sign", -1.5, "-1.5"),
    ("signed zero keeps its sign", -0.0, "-0.0"),
    ("a whole-valued float keeps its trailing .0", 100.0, "100.0"),
    (
        "large float uses exponent notation, matching Postgres float8 text",
        1e16,
        "1e+16",
    ),
    ("fractional large float keeps its significant digits", 1.1e16, "1.1e+16"),
    ("small float uses exponent notation with a zero-padded exponent", 1e-7, "1e-07"),
    ("small float below the expand threshold stays in exponent form", 1e-6, "1e-06"),
    ("large float above 1e21 uses exponent notation", 1e21, "1e+21"),
    ("smallest subnormal float", 5e-324, "5e-324"),
    ("nan is not finite but still renders", float("nan"), "nan"),
    ("positive infinity renders", float("inf"), "inf"),
    ("negative infinity is not formula-guarded", float("-inf"), "-inf"),
    ("Decimal keeps its scale, unlike float", Decimal("1.50"), "1.50"),
    ("raw bytes render as a Postgres bytea hex literal", b"\x01\x02", "\\x0102"),
    (
        "datetime is ISO 8601",
        datetime.datetime(2024, 1, 2, 3, 4, 5),
        "2024-01-02T03:04:05",
    ),
    ("date is ISO 8601", datetime.date(2024, 1, 2), "2024-01-02"),
    ("time is ISO 8601", datetime.time(3, 4, 5), "03:04:05"),
    ("numeric string preserved (negative decimal)", "-5.5", "-5.5"),
    ("numeric string preserved (exponent)", "1e10", "1e10"),
    ("numeric string preserved (leading dot)", ".5", ".5"),
    (
        "big numeric string left intact (numeric literal, not formula-guarded)",
        "123456789012345678901234567890",
        "123456789012345678901234567890",
    ),
    ("formula = is guarded", "=1+1", "'=1+1"),
    ("formula + is guarded", "+1", "'+1"),
    ("formula @ is guarded", "@SUM(A1)", "'@SUM(A1)"),
    ("leading - on non-numeric text is guarded", "-cmd", "'-cmd"),
    ("number-looking but non-numeric leading - is guarded", "-1+1", "'-1+1"),
    ("leading tab is guarded, and needs no CSV quoting", "\tcmd", "'\tcmd"),
    (
        # The guard and the quoting are independent: \r is a formula prefix *and*
        # part of csv.writer's line terminator, so it picks up both treatments.
        "leading CR is guarded and quoted",
        "\rcmd",
        '"\'\rcmd"',
    ),
    ("value with a comma is quoted", "a,b", '"a,b"'),
    ("embedded double quotes are doubled and quoted", 'say "hi"', '"say ""hi"""'),
    ("embedded newline is quoted", "line1\nline2", '"line1\nline2"'),
    ("guarded and quoted together (leading - plus comma)", "-5,5", '"\'-5,5"'),
    ("object serialises to compact JSON, then quoted", {"x": 1}, '"{""x"":1}"'),
    ("array serialises to compact JSON, then quoted", [1, 2], '"[1,2]"'),
    ("non-ASCII text passes through literally (no \\uXXXX escaping)", "café", "café"),
    (
        "object with non-ASCII text stays literal in JSON (ensure_ascii=False)",
        {"name": "José"},
        '"{""name"":""José""}"',
    ),
]

# Whole-record shape, as (description, columns, rows, expected). Cell vectors cannot
# cover this because each is wrapped in a fixed two-column row.
CSV_ROW_VECTORS = [
    (
        "header then one CRLF-terminated line per row",
        ["id", "name"],
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        "id,name\r\n1,Alice\r\n2,Bob\r\n",
    ),
    (
        'a lone empty field is written as "" (not a bare line), as csv.writer does',
        ["a"],
        [{"a": None}],
        'a\r\n""\r\n',
    ),
    ("a lone non-empty field is not quoted", ["a"], [{"a": "x"}], "a\r\nx\r\n"),
    (
        "single column mixes quoted-empty and plain rows",
        ["a"],
        [{"a": "x"}, {"a": None}, {"a": "y"}],
        'a\r\nx\r\n""\r\ny\r\n',
    ),
    (
        "an all-empty multi-column row is a bare separator, never quoted",
        ["a", "b"],
        [{"a": None, "b": None}],
        "a,b\r\n,\r\n",
    ),
]


class CsvCellSerialisationTest(TestCase):
    """Cover ``stringify_cell`` / ``_csv_line`` against the vectors above."""

    def test_matches_cell_vectors(self):
        # Each value sits in a two-column row (with a constant sentinel) so the
        # vector stays focused on cell content; whole-record shape — including
        # the lone-empty-field case where csv.writer emits "" — is pinned
        # separately in test_matches_row_vectors.
        writer = csv.writer(Echo())
        header_line = _csv_line(writer, ["a", "b"])
        for description, value, expected in CSV_CELL_VECTORS:
            with self.subTest(vector=description):
                row_line = _csv_line(writer, [value, "x"])
                self.assertEqual(f"a,b\r\n{expected},x\r\n", header_line + row_line)

    def test_matches_row_vectors(self):
        # Whole-record shape, which the cell vectors cannot cover. Most important
        # is the single-column empty row: csv.writer renders a lone empty field
        # as "" (not a bare line), which a naive "".join of cells would get wrong.
        for description, columns, rows, expected in CSV_ROW_VECTORS:
            with self.subTest(vector=description):
                writer = csv.writer(Echo())
                output = _csv_line(writer, columns)
                for row in rows:
                    output += _csv_line(writer, [row[column] for column in columns])
                self.assertEqual(expected, output)


class AsyncStreamingCsvResponseTest(TestCase):
    @staticmethod
    def _collect(response) -> bytes:
        # The response is an async stream (what actually streams under ASGI), so
        # consume it through an event loop rather than a plain join.
        async def collect():
            return b"".join([chunk async for chunk in response.streaming_content])

        return async_to_sync(collect)()

    def test_streams_the_file_as_a_csv_attachment(self):
        async def batches():
            yield [["1", "2"], ["3", "4"]]

        response = async_streaming_csv_response(
            header=["a", "b"],
            row_batches=batches(),
            filename="query-results.csv",
        )
        self.assertEqual(
            'attachment; filename="query-results.csv"',
            response.headers["Content-Disposition"],
        )
        self.assertEqual(
            UTF8_BOM + "a,b\r\n1,2\r\n3,4\r\n",
            self._collect(response).decode("utf-8"),
        )

    def test_on_finish_runs_once_when_the_stream_is_consumed(self):
        # on_finish ties resource release to the stream's lifetime, so it must not
        # fire until the response is actually consumed, and then exactly once.
        calls = []

        async def batches():
            yield [["1"]]

        response = async_streaming_csv_response(
            header=["a"],
            row_batches=batches(),
            filename="query-results.csv",
            on_finish=lambda: calls.append(1),
        )
        self.assertEqual([], calls)
        self._collect(response)
        self.assertEqual([1], calls)

    def test_row_error_surfaces_from_the_stream(self):
        # A mid-iteration failure cannot be caught before the response is built: it
        # surfaces while the stream is consumed (the view observes this via
        # _tracked_row_batches). Here we only assert the exception is not swallowed.
        async def batches():
            yield [["ok"]]
            raise RuntimeError("mid-iteration failure")

        response = async_streaming_csv_response(
            header=["a"],
            row_batches=batches(),
            filename="query-results.csv",
        )
        with self.assertRaises(RuntimeError):
            self._collect(response)

    def test_close_runs_cleanup_when_the_stream_was_never_consumed(self):
        # On a client disconnect Django calls response.close() without the stream
        # being exhausted. The async generator's own finally would only run at
        # garbage-collection time, so cleanup hangs off close() instead — proven
        # here with no consumption at all, so it cannot be the finally doing it.
        events = []

        async def batches():
            yield [["1"]]

        response = async_streaming_csv_response(
            header=["a"],
            row_batches=batches(),
            filename="query-results.csv",
            on_finish=lambda: events.append("on_finish"),
        )
        response.close()
        self.assertEqual(["on_finish"], events)

    def test_on_finish_runs_once_when_consumed_and_then_closed(self):
        # Normal completion runs cleanup via the generator's finally; Django then
        # also calls close(). The once-guard must keep on_finish to a single call
        # — a BoundedSemaphore.release(), for one, raises on a double release.
        calls = []

        async def batches():
            yield [["1"]]

        response = async_streaming_csv_response(
            header=["a"],
            row_batches=batches(),
            filename="query-results.csv",
            on_finish=lambda: calls.append(1),
        )
        self._collect(response)
        response.close()
        self.assertEqual([1], calls)
