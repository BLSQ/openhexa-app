from hexa.core.test import GraphQLTestCase
from hexa.data_studio.models import QueryLog
from hexa.data_studio.pagination import InvalidPagination
from hexa.data_studio.query_runner import run_saved_query
from hexa.databases.query_text import OrderBy, OrderByDirectionEnum
from hexa.databases.tests.helpers import provision_workspace_database, seed_demo_table

from .testutils import SavedQueryTestMixin


class RunSavedQueryTest(SavedQueryTestMixin, GraphQLTestCase):
    """The runner's contract: what it wraps, what it logs, what ``page_info`` says."""

    ROWS = [(1, "apple"), (2, "banana"), (3, "cherry"), (4, "date"), (5, "avocado")]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        provision_workspace_database(cls, cls.WORKSPACE)

    def setUp(self):
        super().setUp()
        seed_demo_table(self.WORKSPACE, self.ROWS)
        self.request = self.mock_request(self.USER_VIEWER)

    def _run(self, content, **kwargs):
        saved_query = self.create_saved_query(content=content)
        return run_saved_query(self.request, saved_query, **kwargs)

    def test_unwrapped_call_reports_only_the_cap(self):
        result = self._run("SELECT id FROM demo ORDER BY id", max_rows=2)

        self.assertEqual([{"id": 1}, {"id": 2}], result["rows"])
        self.assertEqual(
            {
                "has_next_page": True,
                "has_previous_page": False,
                "page_number": None,
                "start_cursor": None,
                "end_cursor": None,
                "total_items": None,
                "total_pages": None,
            },
            result["page_info"],
        )

    def test_offset_walk(self):
        content = "SELECT id, label FROM demo"
        order_by = [OrderBy(column="label")]
        seen = []
        for page in (1, 2, 3):
            result = self._run(content, order_by=order_by, per_page=2, page=page)
            seen.extend(row["label"] for row in result["rows"])
            info = result["page_info"]
            self.assertEqual(page, info["page_number"])
            self.assertEqual(page > 1, info["has_previous_page"])
            self.assertEqual(page < 3, info["has_next_page"])
        self.assertEqual(["apple", "avocado", "banana", "cherry", "date"], seen)

    def test_cursor_walk_matches_the_offset_walk(self):
        content = "SELECT id, label FROM demo"
        order_by = [
            OrderBy(column="label", direction=OrderByDirectionEnum.DESC),
            OrderBy(column="id"),
        ]
        seen, after = [], None
        while True:
            result = self._run(content, order_by=order_by, per_page=2, after=after)
            seen.extend(row["label"] for row in result["rows"])
            info = result["page_info"]
            self.assertEqual(after is not None, info["has_previous_page"])
            # The first request names no mode, so it is page 1 of both.
            self.assertEqual(1 if after is None else None, info["page_number"])
            if not info["has_next_page"]:
                self.assertIsNone(info["end_cursor"])
                break
            after = info["end_cursor"]
        self.assertEqual(["date", "cherry", "banana", "avocado", "apple"], seen)

    def test_backward_cursor_walk_retraces_the_forward_walk(self):
        content = "SELECT id, label FROM demo"
        order_by = [
            OrderBy(column="label", direction=OrderByDirectionEnum.DESC),
            OrderBy(column="id"),
        ]
        forward = [self._run(content, order_by=order_by, per_page=2)]
        while forward[-1]["page_info"]["has_next_page"]:
            after = forward[-1]["page_info"]["end_cursor"]
            forward.append(
                self._run(content, order_by=order_by, per_page=2, after=after)
            )
        self.assertEqual(3, len(forward))

        backward = [forward[-1]]
        while backward[-1]["page_info"]["has_previous_page"]:
            before = backward[-1]["page_info"]["start_cursor"]
            result = self._run(content, order_by=order_by, per_page=2, before=before)
            self.assertTrue(result["page_info"]["has_next_page"])
            self.assertIsNone(result["page_info"]["page_number"])
            backward.append(result)

        self.assertEqual(
            [page["rows"] for page in forward],
            [page["rows"] for page in reversed(backward)],
        )
        self.assertIsNone(backward[-1]["page_info"]["start_cursor"])

    def test_a_literal_percent_survives_wrapping(self):
        content = "SELECT id FROM demo WHERE label LIKE '%an%' ORDER BY id"

        plain = self._run(content)
        paged = self._run(content, order_by=[OrderBy(column="id")], per_page=10)

        self.assertEqual([{"id": 2}], plain["rows"])
        self.assertEqual(plain["rows"], paged["rows"])

    def test_total_items(self):
        result = self._run(
            "SELECT id FROM demo", per_page=2, page=1, include_total_items=True
        )

        self.assertEqual(5, result["page_info"]["total_items"])
        self.assertEqual(3, result["page_info"]["total_pages"])
        self.assertEqual(2, result["row_count"])

    def test_null_sort_key_yields_no_cursor_but_a_working_page(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, None), (3, "c")])
        order_by = [OrderBy(column="label", direction=OrderByDirectionEnum.DESC)]

        result = self._run("SELECT id, label FROM demo", order_by=order_by, per_page=1)

        # NULLs sort first in DESC, so the page ends on the NULL row.
        self.assertEqual([{"id": 2, "label": None}], result["rows"])
        self.assertTrue(result["page_info"]["has_next_page"])
        self.assertIsNone(result["page_info"]["end_cursor"])

    def test_logs_the_raw_text_of_a_paginated_run(self):
        content = "SELECT id FROM demo"

        self._run(content, order_by=[OrderBy(column="id")], per_page=2, page=2)

        log = QueryLog.objects.get()
        self.assertEqual(QueryLog.Status.SUCCESS, log.status)
        self.assertEqual(content, log.query)
        self.assertEqual(2, log.row_count)
        self.assertTrue(log.truncated)

    def test_rejected_pagination_is_logged(self):
        with self.assertRaises(InvalidPagination):
            self._run("SELECT id FROM demo", page=0)

        log = QueryLog.objects.get()
        self.assertEqual(QueryLog.Status.REJECTED, log.status)
        self.assertIn("page", log.error_message)

    def test_explain_runs_bare_and_refuses_to_page(self):
        content = "EXPLAIN SELECT id FROM demo"

        bare = self._run(content, per_page=1)
        self.assertEqual(["QUERY PLAN"], bare["columns"])
        self.assertFalse(bare["page_info"]["has_next_page"])

        with self.assertRaises(InvalidPagination):
            self._run(content, page=1)
