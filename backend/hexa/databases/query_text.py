"""Preparation of the SQL text submitted by clients, before it reaches PostgreSQL."""

import enum
import re
import unicodedata
from dataclasses import dataclass, replace

import sqlparse
from psycopg2 import sql
from psycopg2.sql import Composable
from sqlparse import tokens
from sqlparse.lexer import Lexer
from sqlparse.sql import Statement, Token


class MultipleStatementsError(Exception):
    """Raised when more than one SQL statement is submitted for execution."""


class OrderByDirectionEnum(enum.Enum):
    ASC = "ASC"
    DESC = "DESC"


# PostgreSQL's lexer accepts these five characters as whitespace and nothing
# else. Every other blank -- non-breaking space, ideographic space, vertical
# tab, ... -- is a syntax error reported at a character the user cannot see,
# and SQL pasted from a chat, a document or a PDF is full of them.
_POSTGRES_WHITESPACE = " \t\n\r\f"

# Whitespace PostgreSQL rejects, plus every non-ASCII character (a cheap filter
# that lets the substitution callback run only where something may be wrong;
# legitimate non-ASCII, e.g. an accented identifier, is returned unchanged).
_SUSPICIOUS_CHARACTER = re.compile(rf"[^\S{_POSTGRES_WHITESPACE}]|[^\x00-\x7f]")

# Literals, quoted identifiers and comments are left verbatim: PostgreSQL
# accepts any character there, so an exotic space is part of the data.
#
# This tuple is also what keeps ``PreparedQuery`` safe: every construct that can
# swallow a semicolon (string, dollar-quoted body, comment) is one of these, so
# cleaning cannot break out of one and expose a statement separator that was not
# there before. Widening it demands a second look at the statement count.
_VERBATIM_TOKEN_TYPES = (tokens.Literal, tokens.Comment)


def _substitute(match: re.Match) -> str:
    character = match.group()
    if unicodedata.category(character) == "Cf":
        # Zero-width and other formatting characters (ZWSP, BOM, soft hyphen,
        # bidi marks): they separate nothing, so dropping them restores the
        # statement the user believes they wrote.
        return ""
    return " " if character.isspace() else character


def _clean(text: str) -> str:
    return _SUSPICIOUS_CHARACTER.sub(_substitute, text)


def _is_verbatim(token_type) -> bool:
    return any(token_type in group for group in _VERBATIM_TOKEN_TYPES)


def sanitize_sql(text: str) -> str:
    """Replace the blanks PostgreSQL cannot parse and drop invisible characters.

    Applies to the whole text, whatever number of statements it holds, and leaves
    literals, quoted identifiers and comments verbatim. Cleaning is idempotent,
    so it can be applied wherever SQL enters the system.
    """
    # Nothing to clean is by far the common case, and answering it costs a scan
    # rather than a trip through sqlparse.
    if not _SUSPICIOUS_CHARACTER.search(text):
        return text
    # Lexing rather than parsing: token types are all the verbatim regions need,
    # and the grouping pass -- the expensive half of a parse -- would add nothing.
    # It also keeps every character, where parsing drops text it reads as no
    # statement at all (a lone exotic blank came back empty).
    lexed = list(Lexer.get_default_instance().get_tokens(text))
    if "".join(value for _, value in lexed) != text:
        # sqlparse is third-party and pinned: should a version ever stop
        # round-tripping its input, clean the text as a whole rather than store
        # or run a statement with pieces missing. Literals pay the price of being
        # cleaned too, which beats losing them.
        return _clean(text)
    return "".join(
        value if _is_verbatim(ttype) else _clean(value) for ttype, value in lexed
    )


def _first_keyword(statement: Statement) -> str | None:
    token = statement.token_first(skip_cm=True)
    # sqlparse wraps some openings (VALUES, a parenthesised query) in a group
    # whose own first token holds the keyword.
    while token is not None and token.is_group:
        token = token.token_first(skip_cm=True)
    return None if token is None else token.normalized.upper()


def _starts_with_explain(statement: Statement) -> bool:
    return _first_keyword(statement) == "EXPLAIN"


# The openings that can stand inside `SELECT * FROM (...) AS q`. Everything else
# (EXPLAIN, SHOW, DO, ...) is a syntax error in a subquery.
_WRAPPABLE_KEYWORDS = frozenset({"SELECT", "WITH", "TABLE", "VALUES"})


def _is_wrappable(statement: Statement) -> bool:
    return _first_keyword(statement) in _WRAPPABLE_KEYWORDS


def _is_blank(token: Token) -> bool:
    return token.is_whitespace or token.ttype in tokens.Comment


def _without_trailing_separator(statement: Statement) -> str:
    """The statement's text with its trailing ``;`` removed.

    The separator is a syntax error once the text is wrapped in a subquery. Only
    whitespace and comments may follow it; anything else and the text is left as
    it is, since it is then not a trailing separator.
    """
    parts = list(statement.tokens)
    for index in range(len(parts) - 1, -1, -1):
        token = parts[index]
        if _is_blank(token):
            continue
        if token.ttype is tokens.Punctuation and token.value == ";":
            del parts[index]
        break
    return "".join(token.value for token in parts)


@dataclass(frozen=True)
class PreparedQuery:
    """A single SQL statement, cleaned of characters PostgreSQL cannot parse.

    ``params`` carries psycopg2's paramstyle contract: ``None`` means ``sql`` is
    raw text to be executed without parameters, a list means ``sql`` is already
    in paramstyle (literal ``%`` doubled, ``%s`` where each value goes). psycopg2
    ``%``-formats a statement whenever it receives parameters, an empty list
    included, so the two must never be mixed.
    """

    sql: str | Composable
    is_explain: bool
    is_wrappable: bool = False
    body: str = ""
    params: list | None = None

    @classmethod
    def from_text(cls, text: str) -> "PreparedQuery":
        """Clean ``text``, then reject input that holds more than one statement.

        Cleaning comes first so that the count, and the EXPLAIN detection with it,
        are established on the exact string PostgreSQL will receive: a verdict
        reached on the raw text would describe a string that is never executed.

        Rejecting stacked statements is load-bearing for the executeSQL endpoint
        (see the tests): it is what prevents a ``SET statement_timeout = 0``
        from being run before the query.
        """
        sql_text = sanitize_sql(text)
        statements = [
            s for s in sqlparse.parse(sql_text) if str(s).strip().rstrip(";").strip()
        ]
        if len(statements) > 1:
            raise MultipleStatementsError(
                "Only a single SQL statement can be executed."
            )
        if not statements:
            return cls(sql=sql_text, is_explain=False)
        statement = statements[0]
        return cls(
            sql=sql_text,
            is_explain=_starts_with_explain(statement),
            is_wrappable=_is_wrappable(statement),
            body=_without_trailing_separator(statement),
        )

    def _inner(self) -> tuple[Composable, list]:
        """The statement as a subquery body, in paramstyle, with its values."""
        if not self.is_wrappable:
            raise ValueError("This statement cannot be wrapped in a subquery.")
        if self.params is None:
            # Raw text: a literal % (a LIKE pattern, say) would be read as a
            # placeholder once the wrapper adds parameters.
            return sql.SQL(self.body.replace("%", "%%")), []
        return sql.SQL(self.body), list(self.params)


@dataclass(frozen=True)
class OrderBy:
    """One sort key: a column, referenced by name."""

    column: str
    direction: OrderByDirectionEnum = OrderByDirectionEnum.ASC

    def _target(self) -> Composable:
        return sql.Identifier(self.column)

    def _clause(self) -> Composable:
        return sql.SQL("{} {}").format(self._target(), sql.SQL(self.direction.value))

    def _comparison(self) -> Composable:
        operator = ">" if self.direction is OrderByDirectionEnum.ASC else "<"
        return sql.SQL("{} {} {}").format(
            self._target(), sql.SQL(operator), sql.Placeholder()
        )


# A newline on each side of the inner text: a trailing line comment would
# otherwise swallow the closing parenthesis.
_SUBQUERY = sql.SQL("SELECT * FROM (\n{inner}\n) AS q")
_COUNT = sql.SQL("SELECT COUNT(*) FROM (\n{inner}\n) AS q")


def _keyset_predicate(order_by: list[OrderBy]) -> tuple[Composable, int]:
    """``(a > %s) OR (a = %s AND b < %s) ...`` for a mixed-direction sort key.

    Returns the predicate and how many placeholders it holds, in the order the
    caller must supply their values: the sort-key values, repeated per branch.
    """
    branches = []
    for index, key in enumerate(order_by):
        equalities = [
            sql.SQL("{} = {}").format(previous._target(), sql.Placeholder())
            for previous in order_by[:index]
        ]
        branches.append(
            sql.SQL("({})").format(
                sql.SQL(" AND ").join([*equalities, key._comparison()])
            )
        )
    return sql.SQL(" OR ").join(branches), sum(range(1, len(order_by) + 1))


def paginate(
    prepared: PreparedQuery,
    *,
    order_by: list[OrderBy] | None,
    per_page: int,
    offset: int | None = None,
    keyset: list | None = None,
) -> PreparedQuery:
    """Wrap ``prepared`` in a sorted, paginated subquery.

    Offset mode (``offset`` given, or neither) emits ``ORDER BY ... LIMIT %s
    OFFSET %s``; cursor mode (``keyset`` given: the previous page's last
    sort-key values, one per ``order_by`` entry) emits a keyset predicate instead
    of the offset. The ``LIMIT`` is ``per_page + 1`` so that the executing side,
    which fetches ``max_rows + 1`` to detect a further page, sees exactly the
    rows the database was asked for.

    The wrapper's values are appended after the ones ``prepared`` carries, so a
    templated statement keeps its placeholders bound in order.
    """
    if per_page < 1:
        raise ValueError("per_page must be at least 1.")
    if offset is not None and keyset is not None:
        raise ValueError("offset and keyset are mutually exclusive.")
    order_by = order_by or []
    inner, params = prepared._inner()
    parts = [_SUBQUERY.format(inner=inner)]
    if keyset is not None:
        if not order_by:
            raise ValueError("A keyset needs an order_by.")
        if len(keyset) != len(order_by):
            raise ValueError("A keyset holds one value per order_by entry.")
        predicate, _ = _keyset_predicate(order_by)
        parts.append(sql.SQL(" WHERE {}").format(predicate))
        for index in range(len(order_by)):
            params.extend(keyset[: index + 1])
    if order_by:
        parts.append(
            sql.SQL(" ORDER BY {}").format(
                sql.SQL(", ").join(key._clause() for key in order_by)
            )
        )
    parts.append(sql.SQL(" LIMIT {}").format(sql.Placeholder()))
    params.append(per_page + 1)
    if keyset is None:
        parts.append(sql.SQL(" OFFSET {}").format(sql.Placeholder()))
        params.append(offset or 0)
    return replace(
        prepared,
        sql=sql.Composed(parts),
        is_explain=False,
        is_wrappable=False,
        body="",
        params=params,
    )


def count_statement(prepared: PreparedQuery) -> PreparedQuery:
    """``SELECT COUNT(*)`` over ``prepared``, for a total row count."""
    inner, params = prepared._inner()
    return replace(
        prepared,
        sql=_COUNT.format(inner=inner),
        is_explain=False,
        is_wrappable=False,
        body="",
        params=params,
    )
