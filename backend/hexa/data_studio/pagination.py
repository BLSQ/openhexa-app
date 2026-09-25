"""Page arbitration for executeSavedQuery: which rows to ask for, in which mode.

This module decides *what* to page from and validates the request; every statement
is written by ``hexa.databases.query_text`` and the cursor by ``.cursor``.
"""

import math
from dataclasses import dataclass

from django.conf import settings

from hexa.databases.query_text import OrderBy, PreparedQuery

from . import cursor as cursor_codec

DEFAULT_PER_PAGE = 50


class PaginationError(Exception):
    """A request that cannot be paged as asked; ``code`` is the ExecuteSQLError value."""

    code = "INVALID_PAGINATION"


class InvalidOrderBy(PaginationError):
    code = "INVALID_ORDER_BY"


class InvalidCursor(PaginationError):
    code = "INVALID_CURSOR"


class InvalidPagination(PaginationError):
    code = "INVALID_PAGINATION"


@dataclass(frozen=True)
class OffsetPage:
    """A page by number. ``order_by`` may be empty; the first page also serves cursor mode."""

    order_by: list[OrderBy]
    per_page: int
    page: int = 1
    include_total: bool = False

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


@dataclass(frozen=True)
class CursorPage:
    """The page past a keyset, which holds one value per ``order_by`` entry.

    ``backward`` is the page *before* the keyset instead: the ``per_page`` rows
    nearest to it, still in ``order_by`` order.
    """

    order_by: list[OrderBy]
    per_page: int
    keyset: list
    backward: bool = False


PageRequest = OffsetPage | CursorPage


def resolve_per_page(per_page: int | None, max_rows: int | None) -> int:
    """The page size, from ``perPage`` or its deprecated alias ``maxRows``.

    Applies to unwrapped calls too, where it is the row cap it always was.
    """
    if per_page is not None and max_rows is not None:
        raise InvalidPagination("maxRows and perPage cannot be combined; use perPage.")
    value = DEFAULT_PER_PAGE if per_page is None and max_rows is None else per_page
    if value is None:
        value = max_rows
    if value < 1:
        raise InvalidPagination("perPage must be at least 1.")
    return min(value, settings.WORKSPACE_DATABASE_QUERY_MAX_ROWS)


def build_page_request(
    prepared: PreparedQuery,
    *,
    order_by: list[OrderBy] | None,
    per_page: int,
    page: int | None,
    after: str | None,
    before: str | None = None,
    include_total_items: bool | None,
) -> PageRequest | None:
    """Validate the pagination arguments; ``None`` when nothing was asked for.

    A call with no ``orderBy``, ``page``, ``after`` or ``before`` runs unwrapped,
    exactly as before this argument set existed. ``orderBy`` alone is the first
    page of both modes.
    """
    order_by = order_by or []
    cursor = after if after is not None else before
    if page is None and cursor is None and not order_by:
        return None
    if not prepared.is_wrappable:
        raise InvalidPagination("This statement cannot be sorted or paginated.")
    if after is not None and before is not None:
        raise InvalidPagination("after and before cannot be combined.")
    if page is not None and cursor is not None:
        raise InvalidPagination("page cannot be combined with a cursor.")
    if cursor is not None:
        if not order_by:
            raise InvalidOrderBy("Cursor pagination requires orderBy.")
        if include_total_items:
            raise InvalidPagination("includeTotalItems is not available with a cursor.")
        try:
            keyset = cursor_codec.decode_cursor(cursor, prepared.body, order_by)
        except cursor_codec.InvalidCursor as e:
            raise InvalidCursor(str(e))
        return CursorPage(
            order_by=order_by,
            per_page=per_page,
            keyset=keyset,
            backward=before is not None,
        )
    if page is not None and page < 1:
        raise InvalidPagination("page must be at least 1.")
    return OffsetPage(
        order_by=order_by,
        per_page=per_page,
        page=page or 1,
        include_total=bool(include_total_items),
    )


def _cursor(request: PageRequest, row: dict | None, sql_text: str, wanted: bool):
    if not (wanted and row is not None and request.order_by):
        return None
    return cursor_codec.encode_cursor(sql_text, request.order_by, row)


def build_page_info(
    request: PageRequest | None,
    *,
    first_row: dict | None,
    last_row: dict | None,
    truncated: bool,
    sql_text: str,
    total_items: int | None = None,
) -> dict:
    """The ``pageInfo`` of a successful result, wrapped or not.

    ``truncated`` is the executing side's "one more row than the page" signal,
    which the wrapper's ``LIMIT per_page + 1`` makes exact: a further page ahead,
    or behind for a backward cursor page. An unwrapped result only knows that.
    ``first_row`` and ``last_row`` are the page's ends as fetched and in display
    order, not their JSON form, so the cursors keep the full precision of the
    sort key. A cursor is only cut for an end that has a page beyond it.
    """
    info = {
        "has_next_page": truncated,
        "has_previous_page": False,
        "page_number": None,
        "start_cursor": None,
        "end_cursor": None,
        "total_items": None,
        "total_pages": None,
    }
    if isinstance(request, OffsetPage):
        info["has_previous_page"] = request.page > 1
        info["page_number"] = request.page
        if total_items is not None:
            info["total_items"] = total_items
            info["total_pages"] = math.ceil(total_items / request.per_page)
    elif isinstance(request, CursorPage):
        # The row the cursor was cut from lies beyond the page, so there is one
        # in that direction (unless it was deleted since, which is harmless).
        if request.backward:
            info["has_next_page"] = True
            info["has_previous_page"] = truncated
        else:
            info["has_previous_page"] = True
    if request is not None:
        info["start_cursor"] = _cursor(
            request, first_row, sql_text, info["has_previous_page"]
        )
        info["end_cursor"] = _cursor(request, last_row, sql_text, info["has_next_page"])
    return info
