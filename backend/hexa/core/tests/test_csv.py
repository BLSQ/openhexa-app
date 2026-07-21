import datetime
import json
from decimal import Decimal
from pathlib import Path

from hexa.core.test import TestCase

from ..csv import (
    UTF8_BOM,
    streaming_csv_response,
    stringify_cell,
)

# Shared with the frontend (DataStudioEditor/csv.parity.test.ts): the single
# source of truth for how a cell must serialise. Both export paths are checked
# against it so the client-side (small results) and server-side (large results)
# CSV builders cannot drift.
CSV_CELL_VECTORS = json.loads(
    (Path(__file__).parent / "fixtures" / "csv_cell_vectors.json").read_text()
)["vectors"]


class CsvCellSerialisationTest(TestCase):
    """The server side of the shared CSV-cell contract (see CSV_CELL_VECTORS).

    The frontend runs the same vectors against ``buildCsv`` in
    ``csv.parity.test.ts``; keeping both green is what guarantees the two
    download paths emit byte-identical files.
    """

    def test_matches_shared_cell_vectors(self):
        # The value sits in a two-column row (with a constant sentinel) rather
        # than alone: csv.writer quotes a *lone* empty field as "" to keep a
        # blank line unambiguous, which the frontend does not — a benign edge
        # (both parse back to empty) that only a single-column result could hit.
        # Testing the realistic multi-column shape keeps the contract meaningful.
        for vector in CSV_CELL_VECTORS:
            with self.subTest(vector=vector["description"]):
                response = streaming_csv_response(
                    header=["a", "b"],
                    rows=[[vector["value"], "x"]],
                    filename="x.csv",
                    with_bom=False,
                )
                body = b"".join(response.streaming_content).decode("utf-8")
                self.assertEqual(f"a,b\r\n{vector['expected']},x\r\n", body)

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


class StreamingCsvResponseTest(TestCase):
    def test_streams_the_file_as_a_csv_attachment(self):
        response = streaming_csv_response(
            header=["a", "b"],
            rows=[["1", "2"], ["3", "4"]],
            filename="query-results.csv",
        )
        body = b"".join(response.streaming_content).decode("utf-8")
        self.assertEqual(UTF8_BOM + "a,b\r\n1,2\r\n3,4\r\n", body)
        self.assertEqual(
            'attachment; filename="query-results.csv"',
            response.headers["Content-Disposition"],
        )

    def test_on_finish_runs_once_when_the_stream_is_consumed(self):
        # on_finish ties resource release to the stream's lifetime, so it must not
        # fire until the response is actually consumed, and then exactly once.
        calls = []
        response = streaming_csv_response(
            header=["a"],
            rows=[["1"]],
            filename="query-results.csv",
            on_finish=lambda: calls.append(1),
        )
        self.assertEqual([], calls)
        b"".join(response.streaming_content)
        self.assertEqual([1], calls)

    def test_row_error_surfaces_from_the_stream(self):
        # With streaming (unlike a buffered response) a mid-iteration failure
        # cannot be caught before the response is built: it surfaces while the
        # stream is consumed. The view observes this via _tracked_rows; here we
        # only assert the exception is not swallowed.
        def rows():
            yield ["ok"]
            raise RuntimeError("mid-iteration failure")

        response = streaming_csv_response(
            header=["a"], rows=rows(), filename="query-results.csv"
        )
        with self.assertRaises(RuntimeError):
            b"".join(response.streaming_content)
