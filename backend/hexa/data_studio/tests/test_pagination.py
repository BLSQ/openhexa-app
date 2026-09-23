from datetime import date, datetime, timezone
from decimal import Decimal

from django.test import SimpleTestCase, override_settings

from hexa.data_studio.cursor import InvalidCursor, decode_cursor, encode_cursor
from hexa.data_studio.pagination import (
    CursorPage,
    InvalidOrderBy,
    InvalidPagination,
    OffsetPage,
    PageRequest,
    build_page_info,
    build_page_request,
    resolve_per_page,
)
from hexa.data_studio.pagination import InvalidCursor as InvalidCursorRequest
from hexa.databases.query_text import OrderBy, OrderByDirectionEnum, PreparedQuery

SQL = "SELECT id, name, born_on FROM people"
ORDER_BY = [
    OrderBy(column="name", direction=OrderByDirectionEnum.DESC),
    OrderBy(column="id"),
]


def _request(**kwargs) -> PageRequest | None:
    arguments = {
        "order_by": None,
        "per_page": 10,
        "page": None,
        "after": None,
        "before": None,
        "include_total_items": None,
    }
    arguments.update(kwargs)
    return build_page_request(PreparedQuery.from_text(SQL), **arguments)


class PerPageTest(SimpleTestCase):
    @override_settings(WORKSPACE_DATABASE_QUERY_MAX_ROWS=1000)
    def test_defaults_and_aliases(self):
        self.assertEqual(50, resolve_per_page(None, None))
        self.assertEqual(20, resolve_per_page(20, None))
        self.assertEqual(30, resolve_per_page(None, 30))

    @override_settings(WORKSPACE_DATABASE_QUERY_MAX_ROWS=100)
    def test_clamps_to_the_hard_limit(self):
        self.assertEqual(100, resolve_per_page(5000, None))
        self.assertEqual(100, resolve_per_page(None, 5000))

    def test_rejects_both_spellings_together(self):
        with self.assertRaises(InvalidPagination):
            resolve_per_page(10, 10)

    def test_rejects_an_empty_page(self):
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(InvalidPagination):
                    resolve_per_page(value, None)
                with self.assertRaises(InvalidPagination):
                    resolve_per_page(None, value)


class PageRequestTest(SimpleTestCase):
    def test_nothing_asked_for_means_unwrapped(self):
        self.assertIsNone(_request())
        self.assertIsNone(_request(order_by=[]))
        self.assertIsNone(_request(include_total_items=True))

    def test_order_by_alone_is_the_first_page(self):
        request = _request(order_by=ORDER_BY)
        self.assertIsInstance(request, OffsetPage)
        self.assertEqual(1, request.page)
        self.assertEqual(0, request.offset)

    def test_offset_mode(self):
        request = _request(page=3, include_total_items=True)
        self.assertIsInstance(request, OffsetPage)
        self.assertEqual([], request.order_by)
        self.assertEqual(20, request.offset)
        self.assertTrue(request.include_total)

    def test_cursor_mode(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        request = _request(order_by=ORDER_BY, after=cursor)
        self.assertIsInstance(request, CursorPage)
        self.assertFalse(request.backward)
        self.assertEqual(["x", 7], request.keyset)

    def test_backward_cursor_mode(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        request = _request(order_by=ORDER_BY, before=cursor)
        self.assertIsInstance(request, CursorPage)
        self.assertTrue(request.backward)
        self.assertEqual(["x", 7], request.keyset)

    def test_reports_a_bad_cursor_with_its_error_code(self):
        for argument in ("after", "before"):
            with self.assertRaises(InvalidCursorRequest) as raised:
                _request(order_by=ORDER_BY, **{argument: "not a cursor"})
            self.assertEqual("INVALID_CURSOR", raised.exception.code)

    def test_rejects_page_and_a_cursor_together(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        for argument in ("after", "before"):
            with self.assertRaises(InvalidPagination):
                _request(order_by=ORDER_BY, page=2, **{argument: cursor})

    def test_rejects_both_cursors_together(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        with self.assertRaises(InvalidPagination):
            _request(order_by=ORDER_BY, after=cursor, before=cursor)

    def test_rejects_a_cursor_without_order_by(self):
        for argument in ("after", "before"):
            with self.assertRaises(InvalidOrderBy):
                _request(**{argument: "anything"})

    def test_rejects_a_total_with_a_cursor(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        for argument in ("after", "before"):
            with self.assertRaises(InvalidPagination):
                _request(
                    order_by=ORDER_BY, include_total_items=True, **{argument: cursor}
                )

    def test_rejects_a_page_below_one(self):
        with self.assertRaises(InvalidPagination):
            _request(page=0)

    def test_rejects_an_unwrappable_statement_only_when_asked_to_page(self):
        explain = PreparedQuery.from_text("EXPLAIN SELECT 1")
        base = {
            "per_page": 10,
            "page": None,
            "after": None,
            "include_total_items": None,
        }
        self.assertIsNone(build_page_request(explain, order_by=None, **base))
        with self.assertRaises(InvalidPagination):
            build_page_request(explain, order_by=ORDER_BY, **base)
        with self.assertRaises(InvalidPagination):
            build_page_request(explain, order_by=None, **{**base, "page": 2})


class CursorTest(SimpleTestCase):
    def test_round_trip(self):
        row = {"id": 7, "name": "x", "born_on": "1990-01-02"}
        cursor = encode_cursor(SQL, ORDER_BY, row)
        self.assertEqual(["x", 7], decode_cursor(cursor, SQL, ORDER_BY))

    def test_carries_values_as_literals_postgresql_coerces_back(self):
        # The row comes as fetched; a timestamp keeps its microseconds, which the
        # JSON form of the result drops, and json/jsonb values travel as text.
        order_by = [OrderBy(column=c) for c in ("born_on", "amount", "at", "doc")]
        row = {
            "born_on": date(1990, 1, 2),
            "amount": Decimal("12.50"),
            "at": datetime(2024, 1, 1, 10, 0, 0, 123456, tzinfo=timezone.utc),
            "doc": {"id": 7},
        }
        cursor = encode_cursor(SQL, order_by, row)
        self.assertEqual(
            ["1990-01-02", "12.50", "2024-01-01T10:00:00.123456+00:00", '{"id": 7}'],
            decode_cursor(cursor, SQL, order_by),
        )

    def test_is_opaque(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        self.assertNotIn("x", cursor.split(":")[0])

    def test_no_cursor_from_a_null_sort_key(self):
        self.assertIsNone(encode_cursor(SQL, ORDER_BY, {"id": 7, "name": None}))
        self.assertIsNone(encode_cursor(SQL, ORDER_BY, {"id": 7}))

    def test_rejects_a_tampered_cursor(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        with self.assertRaises(InvalidCursor):
            decode_cursor(cursor[:-2] + "zz", SQL, ORDER_BY)
        with self.assertRaises(InvalidCursor):
            decode_cursor("not a cursor", SQL, ORDER_BY)

    def test_rejects_a_cursor_for_another_query(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        with self.assertRaises(InvalidCursor):
            decode_cursor(cursor, SQL + " WHERE id > 0", ORDER_BY)

    def test_rejects_a_cursor_for_another_ordering(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        reversed_direction = [OrderBy(column="name"), OrderBy(column="id")]
        with self.assertRaises(InvalidCursor):
            decode_cursor(cursor, SQL, reversed_direction)
        with self.assertRaises(InvalidCursor):
            decode_cursor(cursor, SQL, ORDER_BY[:1])


class PageInfoTest(SimpleTestCase):
    FIRST_ROW = {"id": 1, "name": "a"}
    LAST_ROW = {"id": 2, "name": "b"}

    def _info(self, request, **kwargs):
        arguments = {
            "first_row": self.FIRST_ROW,
            "last_row": self.LAST_ROW,
            "truncated": True,
            "sql_text": SQL,
        }
        arguments.update(kwargs)
        return build_page_info(request, **arguments)

    def _keys(self, cursor):
        return decode_cursor(cursor, SQL, ORDER_BY)

    def test_unwrapped_result(self):
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
            self._info(None),
        )

    def test_first_page_serves_both_modes(self):
        info = self._info(OffsetPage(order_by=ORDER_BY, per_page=2))
        self.assertEqual(1, info["page_number"])
        self.assertFalse(info["has_previous_page"])
        self.assertIsNone(info["start_cursor"])
        self.assertEqual(["b", 2], self._keys(info["end_cursor"]))

    def test_offset_page_with_total(self):
        info = self._info(
            OffsetPage(order_by=[], per_page=2, page=3, include_total=True),
            truncated=False,
            total_items=5,
        )
        self.assertEqual(3, info["page_number"])
        self.assertTrue(info["has_previous_page"])
        self.assertFalse(info["has_next_page"])
        # A page before, but no ordering to cut a cursor from.
        self.assertIsNone(info["start_cursor"])
        self.assertIsNone(info["end_cursor"])
        self.assertEqual(5, info["total_items"])
        self.assertEqual(3, info["total_pages"])

    def test_a_sorted_middle_page_cuts_both_cursors(self):
        info = self._info(OffsetPage(order_by=ORDER_BY, per_page=2, page=2))
        self.assertEqual(["a", 1], self._keys(info["start_cursor"]))
        self.assertEqual(["b", 2], self._keys(info["end_cursor"]))

    def test_cursor_page(self):
        info = self._info(CursorPage(order_by=ORDER_BY, per_page=2, keyset=["z", 0]))
        self.assertIsNone(info["page_number"])
        self.assertTrue(info["has_previous_page"])
        self.assertTrue(info["has_next_page"])
        self.assertEqual(["a", 1], self._keys(info["start_cursor"]))
        self.assertEqual(["b", 2], self._keys(info["end_cursor"]))

    def test_backward_cursor_page(self):
        request = CursorPage(
            order_by=ORDER_BY, per_page=2, keyset=["c", 3], backward=True
        )

        # The row the cursor came from lies ahead; ``truncated`` now means behind.
        middle = self._info(request)
        self.assertTrue(middle["has_next_page"])
        self.assertTrue(middle["has_previous_page"])
        self.assertEqual(["a", 1], self._keys(middle["start_cursor"]))
        self.assertEqual(["b", 2], self._keys(middle["end_cursor"]))

        first = self._info(request, truncated=False)
        self.assertTrue(first["has_next_page"])
        self.assertFalse(first["has_previous_page"])
        self.assertIsNone(first["start_cursor"])
        self.assertEqual(["b", 2], self._keys(first["end_cursor"]))

    def test_no_cursor_beyond_the_ends_or_from_a_null_key(self):
        request = OffsetPage(order_by=ORDER_BY, per_page=2)
        last = self._info(request, truncated=False)
        self.assertIsNone(last["end_cursor"])
        nulled = self._info(request, last_row={"id": 1, "name": None})
        self.assertTrue(nulled["has_next_page"])
        self.assertIsNone(nulled["end_cursor"])

        forward = CursorPage(order_by=ORDER_BY, per_page=2, keyset=["z", 0])
        nulled_start = self._info(forward, first_row={"id": 1, "name": None})
        self.assertTrue(nulled_start["has_previous_page"])
        self.assertIsNone(nulled_start["start_cursor"])
