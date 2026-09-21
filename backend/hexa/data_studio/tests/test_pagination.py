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
        self.assertEqual(["x", 7], request.keyset)

    def test_reports_a_bad_cursor_with_its_error_code(self):
        with self.assertRaises(InvalidCursorRequest) as raised:
            _request(order_by=ORDER_BY, after="not a cursor")
        self.assertEqual("INVALID_CURSOR", raised.exception.code)

    def test_rejects_page_and_after_together(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        with self.assertRaises(InvalidPagination):
            _request(order_by=ORDER_BY, page=2, after=cursor)

    def test_rejects_a_cursor_without_order_by(self):
        with self.assertRaises(InvalidOrderBy):
            _request(after="anything")

    def test_rejects_a_total_with_a_cursor(self):
        cursor = encode_cursor(SQL, ORDER_BY, {"id": 7, "name": "x"})
        with self.assertRaises(InvalidPagination):
            _request(order_by=ORDER_BY, after=cursor, include_total_items=True)

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

    def test_carries_the_serialised_values_as_they_are(self):
        # Rows reach this module already JSON-safe (dates and decimals as
        # strings), and PostgreSQL coerces those literals back to the column type.
        order_by = [OrderBy(column="born_on"), OrderBy(column="amount")]
        row = {"born_on": "1990-01-02", "amount": "12.50"}
        cursor = encode_cursor(SQL, order_by, row)
        self.assertEqual(["1990-01-02", "12.50"], decode_cursor(cursor, SQL, order_by))

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
    ROWS = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]

    def test_unwrapped_result(self):
        self.assertEqual(
            {
                "has_next_page": True,
                "has_previous_page": False,
                "page_number": None,
                "end_cursor": None,
                "total_items": None,
                "total_pages": None,
            },
            build_page_info(None, rows=self.ROWS, has_next=True, sql_text=SQL),
        )

    def test_first_page_serves_both_modes(self):
        info = build_page_info(
            OffsetPage(order_by=ORDER_BY, per_page=2),
            rows=self.ROWS,
            has_next=True,
            sql_text=SQL,
        )
        self.assertEqual(1, info["page_number"])
        self.assertFalse(info["has_previous_page"])
        self.assertEqual(["b", 2], decode_cursor(info["end_cursor"], SQL, ORDER_BY))

    def test_offset_page_with_total(self):
        info = build_page_info(
            OffsetPage(order_by=[], per_page=2, page=3, include_total=True),
            rows=self.ROWS,
            has_next=False,
            sql_text=SQL,
            total_items=5,
        )
        self.assertEqual(3, info["page_number"])
        self.assertTrue(info["has_previous_page"])
        self.assertFalse(info["has_next_page"])
        self.assertIsNone(info["end_cursor"])
        self.assertEqual(5, info["total_items"])
        self.assertEqual(3, info["total_pages"])

    def test_cursor_page(self):
        info = build_page_info(
            CursorPage(order_by=ORDER_BY, per_page=2, keyset=["z", 0]),
            rows=self.ROWS,
            has_next=True,
            sql_text=SQL,
        )
        self.assertIsNone(info["page_number"])
        self.assertTrue(info["has_previous_page"])
        self.assertIsNotNone(info["end_cursor"])

    def test_no_cursor_on_the_last_page_or_a_null_key(self):
        request = OffsetPage(order_by=ORDER_BY, per_page=2)
        last = build_page_info(request, rows=self.ROWS, has_next=False, sql_text=SQL)
        self.assertIsNone(last["end_cursor"])
        nulled = build_page_info(
            request, rows=[{"id": 1, "name": None}], has_next=True, sql_text=SQL
        )
        self.assertTrue(nulled["has_next_page"])
        self.assertIsNone(nulled["end_cursor"])
