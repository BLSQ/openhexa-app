import csv
import datetime
import json
from decimal import Decimal
from pathlib import Path

from asgiref.sync import async_to_sync

from hexa.core.test import TestCase

from ..csv import (
    UTF8_BOM,
    Echo,
    _csv_line,
    async_streaming_csv_response,
    stringify_cell,
)

# Shared with the frontend (DataStudioEditor/csv.parity.test.ts): the single
# source of truth for how a cell must serialise. Both export paths are checked
# against it so the client-side (small results) and server-side (large results)
# CSV builders cannot drift.
_CSV_CONTRACT = json.loads(
    (Path(__file__).parent / "fixtures" / "csv_cell_vectors.json").read_text()
)
CSV_CELL_VECTORS = _CSV_CONTRACT["vectors"]
CSV_ROW_VECTORS = _CSV_CONTRACT["rowVectors"]


class CsvCellSerialisationTest(TestCase):
    """The server side of the shared CSV-cell contract (see CSV_CELL_VECTORS).

    The frontend runs the same vectors against ``buildCsv`` in
    ``csv.parity.test.ts``; keeping both green is what guarantees the two
    download paths emit byte-identical files.
    """

    def test_matches_shared_cell_vectors(self):
        # Each value sits in a two-column row (with a constant sentinel) so the
        # vector stays focused on cell content; whole-record shape — including
        # the lone-empty-field case where csv.writer emits "" — is pinned
        # separately in test_matches_shared_row_vectors.
        writer = csv.writer(Echo())
        header_line = _csv_line(writer, ["a", "b"])
        for vector in CSV_CELL_VECTORS:
            with self.subTest(vector=vector["description"]):
                row_line = _csv_line(writer, [vector["value"], "x"])
                self.assertEqual(
                    f"a,b\r\n{vector['expected']},x\r\n", header_line + row_line
                )

    def test_matches_shared_row_vectors(self):
        # Whole-record shape, which the cell vectors cannot cover. Most important
        # is the single-column empty row: csv.writer renders a lone empty field
        # as "" (not a bare line), and the frontend buildCsv now matches that, so
        # a single-column result is byte-identical across both export paths.
        for vector in CSV_ROW_VECTORS:
            with self.subTest(vector=vector["description"]):
                writer = csv.writer(Echo())
                columns = vector["columns"]
                output = _csv_line(writer, columns)
                for row in vector["rows"]:
                    output += _csv_line(writer, [row[column] for column in columns])
                self.assertEqual(vector["expected"], output)

    def test_backend_only_types(self):
        # Types that never cross the GraphQL wire as-is (the interactive result
        # already encodes them), so they cannot appear in the shared fixture.
        self.assertEqual("\\x0102", stringify_cell(b"\x01\x02"))
        self.assertEqual("1.50", stringify_cell(Decimal("1.50")))
        self.assertEqual(
            "2024-01-02T03:04:05",
            stringify_cell(datetime.datetime(2024, 1, 2, 3, 4, 5)),
        )
        self.assertEqual("2024-01-02", stringify_cell(datetime.date(2024, 1, 2)))

    def test_float_formatting_matches_javascript(self):
        # Floats cross the interactive path as JSON numbers and are rendered with
        # String(x) client-side, so the server export must match ECMA-262's
        # Number.toString. Non-finite and signed-zero cases cannot live in the
        # JSON fixture (not representable / not distinguishable), so pin them here.
        self.assertEqual("NaN", stringify_cell(float("nan")))
        self.assertEqual("Infinity", stringify_cell(float("inf")))
        self.assertEqual("-Infinity", stringify_cell(float("-inf")))
        self.assertEqual("0", stringify_cell(-0.0))
        self.assertEqual("-1.5", stringify_cell(-1.5))
        self.assertEqual("10000000000000000", stringify_cell(1e16))
        self.assertEqual("1e-7", stringify_cell(1e-7))
        self.assertEqual("0.000001", stringify_cell(1e-6))
        self.assertEqual("1e+21", stringify_cell(1e21))
        self.assertEqual("5e-324", stringify_cell(5e-324))
        self.assertEqual("100", stringify_cell(100.0))


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
