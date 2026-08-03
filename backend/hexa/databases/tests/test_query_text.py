import unittest

from hexa.databases.query_text import (
    MultipleStatementsError,
    PreparedQuery,
    sanitize_sql,
)

NBSP = "\u00a0"
ZWSP = "\u200b"
BOM = "\ufeff"
IDEOGRAPHIC_SPACE = "\u3000"


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
