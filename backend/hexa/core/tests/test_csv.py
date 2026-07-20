import datetime
import json
from decimal import Decimal
from pathlib import Path

from django.http import StreamingHttpResponse

from hexa.core.test import TestCase
from hexa.user_management.models import Membership, Team, User

from ..csv import (
    UTF8_BOM,
    buffered_csv_response,
    render_queryset_to_csv,
    stream_csv,
    stringify_cell,
)

# Shared with the frontend (DataStudioEditor/csv.parity.test.ts): the single
# source of truth for how a cell must serialise. Both export paths are checked
# against it so the client-side (small results) and server-side (large results)
# CSV builders cannot drift.
CSV_CELL_VECTORS = json.loads(
    (Path(__file__).parent / "fixtures" / "csv_cell_vectors.json").read_text()
)["vectors"]


class CsvTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim",
        )
        user_2 = User.objects.create_user(
            "mary@bluesquarehub.com",
            "mary",
        )
        team = Team.objects.create(name="Tèst Teâm")
        cls.MEMBERSHIP_1 = Membership.objects.create(team=team, user=user_1)
        cls.MEMBERSHIP_2 = Membership.objects.create(team=team, user=user_2)

    def test_render_queryset_to_csv(self):
        response = render_queryset_to_csv(
            Membership.objects.order_by("user__email"),
            filename="memberships.csv",
            field_names=[
                "id",
                "team.name",
                "user.email",
                "user.first_name",
                "user.foo.bar",
            ],
        )
        self.assertIsInstance(response, StreamingHttpResponse)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            'attachment; filename="memberships.csv"',
            response.headers["Content-Disposition"],
        )
        content = b"".join(response.streaming_content)
        self.assertEqual(
            (
                UTF8_BOM + "id,team_name,user_email,user_first_name,user_foo_bar\r\n"
                f"{self.MEMBERSHIP_1.id},Tèst Teâm,jim@bluesquarehub.com,,\r\n"
                f"{self.MEMBERSHIP_2.id},Tèst Teâm,mary@bluesquarehub.com,,\r\n"
            ).encode(),
            content,
        )


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
                response = stream_csv(
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


class BufferedCsvResponseTest(TestCase):
    def test_writes_the_whole_file_as_an_attachment(self):
        response = buffered_csv_response(
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
        # A definite size (vs chunked streaming) lets the browser itself detect a
        # truncated transfer.
        self.assertIn("Content-Length", response.headers)

    def test_row_error_propagates_before_any_response(self):
        # The whole point of buffering: a failure mid-iteration must raise here,
        # not silently truncate an already-started download.
        def rows():
            yield ["ok", "x"]
            raise RuntimeError("mid-iteration failure")

        with self.assertRaises(RuntimeError):
            buffered_csv_response(
                header=["a", "b"], rows=rows(), filename="query-results.csv"
            )
