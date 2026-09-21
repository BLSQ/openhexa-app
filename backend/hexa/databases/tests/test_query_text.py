import unittest
from unittest import mock

import psycopg2
from django.db import connection
from sqlparse import tokens
from sqlparse.lexer import Lexer

from hexa.databases.query_text import (
    MultipleStatementsError,
    OrderBy,
    OrderByDirectionEnum,
    PreparedQuery,
    count_statement,
    paginate,
    sanitize_sql,
)

NBSP = "\u00a0"
ZWSP = "\u200b"
BOM = "\ufeff"
IDEOGRAPHIC_SPACE = "\u3000"


class _LosingLexer:
    """A lexer that drops a token, i.e. the failure the fallback exists for."""

    def get_tokens(self, text: str, encoding=None):
        yield tokens.Keyword.DML, text[:-1]


class StatementCountTest(unittest.TestCase):
    """Direct coverage of the single-statement rule.

    This single check is load-bearing for two separate guarantees of the
    executeSQL endpoint:

      1. The per-call statement_timeout cannot be defeated, because the only way
         to raise it is to run `SET statement_timeout = ...` as a *separate*
         statement before the query (statement_timeout is a USERSET GUC).
      2. No write/DDL can be smuggled in alongside a read (the role blocks the
         write itself, but stacking is the first line of defence).

    Both rely entirely on sqlparse splitting statements exactly the way
    PostgreSQL does. sqlparse is a third-party parser pinned in requirements.txt;
    an upgrade could silently change its splitting of dollar-quotes, string
    literals or comments and quietly weaken the endpoint. These tests turn that
    parser-version dependency into something CI will catch -- they don't need a
    database, so they stay fast.
    """

    def test_allows_single_statements_with_embedded_semicolons(self):
        # Semicolons inside string literals, dollar-quoted bodies, and trailing
        # comments must NOT be mistaken for statement separators.
        allowed = [
            "SELECT 1 AS id;",
            "SELECT 'a;b' AS x",
            "SELECT $tag$ a ; b ; c $tag$ AS x",
            "SELECT 1 AS id; -- SELECT pg_sleep(3)",
            "DO $$ BEGIN PERFORM 1; PERFORM 2; END $$;",
        ]
        for query in allowed:
            with self.subTest(query=query):
                PreparedQuery.from_text(query)

    def test_rejects_stacked_statements(self):
        # The security-critical case is the first one: a SET that would disable
        # the timeout, followed by an unbounded query. The rest are syntactic
        # variations that must not slip a second statement past the parser.
        rejected = [
            "SET statement_timeout = 0; SELECT pg_sleep(3)",
            "SELECT 1;SELECT 2",
            "SET statement_timeout = 0\n;\nSELECT pg_sleep(3)",
            "SET statement_timeout = 0 /* ; */ ; SELECT pg_sleep(3)",
            "SELECT $tag$ x $tag$; SELECT pg_sleep(3)",
            "SELECT 'a;b'; SELECT pg_sleep(3)",
        ]
        for query in rejected:
            with self.subTest(query=query):
                with self.assertRaises(MultipleStatementsError):
                    PreparedQuery.from_text(query)

    def test_counts_the_statements_of_the_query_it_returns(self):
        # The count has to be reached on the cleaned text, because that is the
        # string PostgreSQL receives. Submitting back what is about to be executed
        # must therefore reach the very same verdict -- were the count taken on the
        # raw text instead, cleaning would be free to change the statement count
        # afterwards and the check would describe a string nobody runs.
        for query in [
            f"SELECT{NBSP}1",
            f"SELECT{NBSP}$tag$ a ; b $tag$",
            f"SELECT{ZWSP} 'a;b' AS x",
            f"EXPLAIN{NBSP}(VERBOSE) SELECT 1",
            f"SELECT 1;{ZWSP}",
            f"--{NBSP}note\nSELECT 1",
        ]:
            with self.subTest(query=query):
                prepared = PreparedQuery.from_text(query)
                self.assertEqual(prepared, PreparedQuery.from_text(prepared.sql))


class SanitizationTest(unittest.TestCase):
    """SQL pasted from a chat, a document or a PDF carries blanks PostgreSQL
    rejects, which it then reports as a syntax error at a character the user
    cannot see. Those are replaced; everything PostgreSQL accepts is untouched.
    """

    def assertSql(self, expected: str, query: str):
        self.assertEqual(expected, sanitize_sql(query))

    def test_replaces_unsupported_blanks(self):
        for blank in [NBSP, IDEOGRAPHIC_SPACE, "\u202f", "\u2009", "\u2028", "\v"]:
            with self.subTest(blank=repr(blank)):
                self.assertSql("SELECT 1", f"SELECT{blank}1")

    def test_removes_invisible_characters(self):
        for invisible in [ZWSP, BOM, "\u2060", "\u00ad"]:
            with self.subTest(invisible=repr(invisible)):
                self.assertSql("SELECT 1", f"SELECT{invisible} 1")

    def test_replaces_blanks_inside_multi_word_keywords(self):
        # sqlparse folds the blank of a multi-word keyword into a single token,
        # so cleaning whitespace tokens alone would leave these broken.
        self.assertSql("SELECT n FROM t ORDER BY n", f"SELECT n FROM t ORDER{NBSP}BY n")
        self.assertSql("SELECT 1 IS NOT NULL", f"SELECT 1 IS{NBSP}NOT{NBSP}NULL")

    def test_keeps_whitespace_postgresql_accepts(self):
        query = "SELECT\t1,\r\n\f  2 FROM t"
        self.assertSql(query, query)

    def test_keeps_literals_comments_and_identifiers_verbatim(self):
        # PostgreSQL accepts any character there, so an exotic blank is data.
        verbatim = [
            f"SELECT 'a{NBSP}b' AS x",
            f'SELECT 1 AS "col{NBSP}x"',
            f"SELECT $tag$a{NBSP}b$tag$",
            f"SELECT E'a{NBSP}b'",
            f"-- note{NBSP}here\nSELECT 1",
            f"/* note{ZWSP}here */ SELECT 1",
            "SELECT 'héllo' AS café",
        ]
        for query in verbatim:
            with self.subTest(query=query):
                self.assertSql(query, query)

    def test_is_idempotent(self):
        once = sanitize_sql(f"SELECT{NBSP}'a{NBSP}b'{ZWSP} FROM t")
        self.assertEqual(once, sanitize_sql(once))

    def test_cleans_every_statement(self):
        # Unlike execution, saving does not require a single statement.
        self.assertSql("SELECT 1; SELECT 2", f"SELECT{NBSP}1;{ZWSP} SELECT{NBSP}2")

    def test_preserves_text_without_a_statement(self):
        for query in ["", "   ", "\n"]:
            with self.subTest(query=repr(query)):
                self.assertSql(query, query)

    def test_drops_nothing_but_the_invisible_characters(self):
        # Reassembling from sqlparse's *statements* silently lost text it read as
        # no statement at all: a lone exotic blank came back as an empty string.
        # Nothing may disappear except the characters meant to.
        self.assertSql(" ", NBSP)
        self.assertSql(" ", IDEOGRAPHIC_SPACE)
        self.assertSql(" ", f"{NBSP}{ZWSP}")
        self.assertSql(" --x", f"{NBSP}--x")

    def test_falls_back_to_cleaning_the_whole_text_if_lexing_loses_content(self):
        # Guards the assumption the reassembly rests on. A parser that stops
        # round-tripping its input must cost us the verbatim regions, never
        # characters of the query itself.
        with mock.patch.object(
            Lexer, "get_default_instance", return_value=_LosingLexer()
        ):
            self.assertSql("SELECT 'a b' FROM t", f"SELECT 'a{NBSP}b'{ZWSP} FROM t")


class ExplainDetectionTest(unittest.TestCase):
    def test_detects_explain(self):
        for query in [
            "EXPLAIN SELECT 1",
            "  explain (verbose)\n  SELECT 1",
            f"EXPLAIN{NBSP}(VERBOSE) SELECT 1",
            "-- a comment\nEXPLAIN SELECT 1",
        ]:
            with self.subTest(query=query):
                self.assertTrue(PreparedQuery.from_text(query).is_explain)

    def test_detects_non_explain(self):
        for query in ["SELECT 1", "WITH t AS (SELECT 1) SELECT * FROM t", ""]:
            with self.subTest(query=query):
                self.assertFalse(PreparedQuery.from_text(query).is_explain)


class WrappabilityTest(unittest.TestCase):
    def test_strips_the_trailing_separator(self):
        for query, body in [
            ("SELECT 1;", "SELECT 1"),
            ("SELECT 1 ;  ", "SELECT 1   "),
            ("SELECT 1; -- SELECT 2", "SELECT 1 -- SELECT 2"),
            ("SELECT 'a;b';", "SELECT 'a;b'"),
            ("SELECT 1", "SELECT 1"),
            ("", ""),
        ]:
            with self.subTest(query=query):
                self.assertEqual(PreparedQuery.from_text(query).body, body)

    def test_allows_the_statements_a_subquery_accepts(self):
        for query in [
            "SELECT 1",
            "select 1",
            "WITH t AS (SELECT 1) SELECT * FROM t",
            "TABLE t",
            "VALUES (1), (2)",
            "-- a comment\nSELECT 1",
            "/* a comment */ SELECT 1",
        ]:
            with self.subTest(query=query):
                self.assertTrue(PreparedQuery.from_text(query).is_wrappable)

    def test_refuses_the_statements_a_subquery_rejects(self):
        for query in ["EXPLAIN SELECT 1", "SHOW all", "DO $$ BEGIN END $$", ""]:
            with self.subTest(query=query):
                self.assertFalse(PreparedQuery.from_text(query).is_wrappable)


class PaginateTest(unittest.TestCase):
    """The wrapper's SQL, checked on the bytes psycopg2 sends.

    These need a connection because ``psycopg2.sql.Identifier`` quotes through
    libpq; no query is run. Workspace databases are reached through psycopg2
    where Django's own connection is psycopg3, so one is opened on the test
    database directly.
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        db = connection.settings_dict
        cls.conn = psycopg2.connect(
            host=db["HOST"],
            port=db["PORT"],
            dbname=db["NAME"],
            user=db["USER"],
            password=db["PASSWORD"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        super().tearDownClass()

    def _render(self, prepared: PreparedQuery) -> str:
        """The exact statement psycopg2 sends, values substituted."""
        with self.conn.cursor() as cursor:
            return cursor.mogrify(prepared.sql, prepared.params).decode()

    def test_offset_mode(self):
        wrapped = paginate(
            PreparedQuery.from_text("SELECT id, name FROM t;"),
            order_by=[
                OrderBy(column="name"),
                OrderBy(column="id", direction=OrderByDirectionEnum.DESC),
            ],
            per_page=10,
            offset=20,
        )
        self.assertEqual(
            self._render(wrapped),
            'SELECT * FROM (\nSELECT id, name FROM t\n) AS q ORDER BY "name" ASC, '
            '"id" DESC LIMIT 11 OFFSET 20',
        )

    def test_limit_is_one_more_than_the_page(self):
        # The executing side fetches max_rows + 1 to detect a further page: a
        # LIMIT of exactly per_page would make hasNextPage always false.
        wrapped = paginate(
            PreparedQuery.from_text("SELECT 1"), order_by=None, per_page=50
        )
        self.assertEqual(wrapped.params, [51, 0])

    def test_offset_mode_without_order_by(self):
        wrapped = paginate(PreparedQuery.from_text("SELECT 1"), order_by=[], per_page=5)
        self.assertEqual(
            self._render(wrapped), "SELECT * FROM (\nSELECT 1\n) AS q LIMIT 6 OFFSET 0"
        )

    def test_cursor_mode_with_mixed_directions(self):
        wrapped = paginate(
            PreparedQuery.from_text("SELECT a, b, c FROM t"),
            order_by=[
                OrderBy(column="a"),
                OrderBy(column="b", direction=OrderByDirectionEnum.DESC),
                OrderBy(column="c"),
            ],
            per_page=10,
            keyset=[1, "two", 3],
        )
        self.assertEqual(
            self._render(wrapped),
            "SELECT * FROM (\nSELECT a, b, c FROM t\n) AS q WHERE "
            '("a" > 1) OR ("a" = 1 AND "b" < \'two\') '
            'OR ("a" = 1 AND "b" = \'two\' AND "c" > 3) '
            'ORDER BY "a" ASC, "b" DESC, "c" ASC LIMIT 11',
        )

    def test_cursor_mode_needs_an_order_by_and_one_value_per_key(self):
        prepared = PreparedQuery.from_text("SELECT a FROM t")
        with self.assertRaises(ValueError):
            paginate(prepared, order_by=[], per_page=10, keyset=[1])
        with self.assertRaises(ValueError):
            paginate(prepared, order_by=[OrderBy(column="a")], per_page=10, keyset=[])

    def test_refuses_offset_and_keyset_together(self):
        with self.assertRaises(ValueError):
            paginate(
                PreparedQuery.from_text("SELECT a FROM t"),
                order_by=[OrderBy(column="a")],
                per_page=10,
                offset=0,
                keyset=[1],
            )

    def test_refuses_an_empty_page(self):
        with self.assertRaises(ValueError):
            paginate(PreparedQuery.from_text("SELECT 1"), order_by=None, per_page=0)

    def test_refuses_an_unwrappable_statement(self):
        with self.assertRaises(ValueError):
            paginate(
                PreparedQuery.from_text("EXPLAIN SELECT 1"), order_by=None, per_page=1
            )

    def test_quotes_a_column_name_as_an_identifier(self):
        wrapped = paginate(
            PreparedQuery.from_text("SELECT 1"),
            order_by=[OrderBy(column='x"; DROP TABLE t; --')],
            per_page=1,
        )
        self.assertIn('ORDER BY "x""; DROP TABLE t; --" ASC', self._render(wrapped))

    def test_doubles_percent_in_raw_text(self):
        # Raw text (params None) is about to be %-formatted for the first time.
        wrapped = paginate(
            PreparedQuery.from_text("SELECT * FROM t WHERE n LIKE '%foo%'"),
            order_by=None,
            per_page=1,
        )
        self.assertIn("LIKE '%foo%'", self._render(wrapped))
        self.assertIn("LIKE '%%foo%%'", wrapped.sql.as_string(self.conn))

    def test_keeps_paramstyle_text_and_appends_its_values(self):
        # Text already in paramstyle is not escaped again, and the wrapper's
        # values come after the ones it was handed.
        prepared = PreparedQuery(
            sql="SELECT * FROM t WHERE n LIKE '%%foo%%' AND id > %s",
            is_explain=False,
            is_wrappable=True,
            body="SELECT * FROM t WHERE n LIKE '%%foo%%' AND id > %s",
            params=[7],
        )
        wrapped = paginate(
            prepared, order_by=[OrderBy(column="id")], per_page=10, keyset=[42]
        )
        self.assertEqual(wrapped.params, [7, 42, 11])
        self.assertEqual(
            self._render(wrapped),
            "SELECT * FROM (\nSELECT * FROM t WHERE n LIKE '%foo%' AND id > 7\n) AS q "
            'WHERE ("id" > 42) ORDER BY "id" ASC LIMIT 11',
        )

    def test_counts_the_inner_query(self):
        counted = count_statement(PreparedQuery.from_text("SELECT 1 AS a; -- tail"))
        self.assertEqual(
            self._render(counted),
            "SELECT COUNT(*) FROM (\nSELECT 1 AS a -- tail\n) AS q",
        )
        self.assertFalse(counted.is_explain)
