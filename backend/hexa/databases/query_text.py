"""Preparation of the SQL text submitted by clients, before it reaches PostgreSQL."""

import re
import unicodedata
from dataclasses import dataclass

import sqlparse
from sqlparse import tokens
from sqlparse.sql import Statement


class MultipleStatementsError(Exception):
    """Raised when more than one SQL statement is submitted for execution."""


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


def _clean_statement(statement: Statement) -> str:
    return "".join(
        token.value if _is_verbatim(token.ttype) else _clean(token.value)
        for token in statement.flatten()
    )


def sanitize_sql(text: str) -> str:
    """Replace the blanks PostgreSQL cannot parse and drop invisible characters.

    Applies to any number of statements, and leaves literals, quoted identifiers
    and comments verbatim. Cleaning is idempotent, so it can be applied wherever
    SQL enters the system.
    """
    # Nothing to clean is by far the common case, and answering it costs a scan
    # rather than a parse.
    if not _SUSPICIOUS_CHARACTER.search(text):
        return text
    return "".join(_clean_statement(statement) for statement in sqlparse.parse(text))


def _starts_with_explain(statement: Statement) -> bool:
    first_token = statement.token_first(skip_cm=True)
    # Cleaned before comparing: sqlparse folds the blank of a multi-word keyword
    # into the token itself, so an exotic space survives in ``normalized``.
    return (
        first_token is not None and _clean(first_token.normalized).upper() == "EXPLAIN"
    )


@dataclass(frozen=True)
class PreparedQuery:
    """A single SQL statement, cleaned of characters PostgreSQL cannot parse."""

    sql: str
    is_explain: bool

    @classmethod
    def from_text(cls, text: str) -> "PreparedQuery":
        """Parse ``text`` once, rejecting input that holds more than one statement.

        Rejecting stacked statements is load-bearing for the executeSQL endpoint
        (see the tests): it is what prevents a ``SET statement_timeout = 0``
        from being run before the query.
        """
        statements = sqlparse.parse(text)
        meaningful = [s for s in statements if str(s).strip().rstrip(";").strip()]
        if len(meaningful) > 1:
            raise MultipleStatementsError(
                "Only a single SQL statement can be executed."
            )
        if not meaningful:
            return cls(sql=text, is_explain=False)
        return cls(
            sql=sanitize_sql(text),
            is_explain=_starts_with_explain(meaningful[0]),
        )
