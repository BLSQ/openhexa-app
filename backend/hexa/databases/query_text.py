"""Preparation of the SQL text submitted by clients, before it reaches PostgreSQL."""

import re
import unicodedata
from dataclasses import dataclass

import sqlparse
from sqlparse import tokens
from sqlparse.lexer import Lexer
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


def _starts_with_explain(statement: Statement) -> bool:
    first_token = statement.token_first(skip_cm=True)
    return first_token is not None and first_token.normalized.upper() == "EXPLAIN"


@dataclass(frozen=True)
class PreparedQuery:
    """A single SQL statement, cleaned of characters PostgreSQL cannot parse."""

    sql: str
    is_explain: bool

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
        sql = sanitize_sql(text)
        statements = [
            s for s in sqlparse.parse(sql) if str(s).strip().rstrip(";").strip()
        ]
        if len(statements) > 1:
            raise MultipleStatementsError(
                "Only a single SQL statement can be executed."
            )
        return cls(
            sql=sql,
            is_explain=bool(statements) and _starts_with_explain(statements[0]),
        )
