import datetime

from django.test import SimpleTestCase

from hexa.data_studio.execution import (
    ParameterError,
    TemplateRenderError,
    render_saved_query,
)
from hexa.data_studio.models import SavedQuery


def make_query(content: str, parameters=None) -> SavedQuery:
    """Build an unsaved SavedQuery; rendering never touches the database."""
    return SavedQuery(content=content, parameters=parameters or [])


class RenderSavedQueryTest(SimpleTestCase):
    def test_no_parameters_passes_sql_through(self):
        query = make_query("SELECT * FROM demo")
        sql, binds = render_saved_query(query)
        self.assertEqual("SELECT * FROM demo", sql)
        self.assertEqual({}, binds)

    def test_value_parameter_is_bound_not_interpolated(self):
        query = make_query(
            "SELECT * FROM demo WHERE country = {{ country }}",
            [{"name": "country", "type": "string", "kind": "value"}],
        )
        sql, binds = render_saved_query(query, {"country": "BE"})
        self.assertEqual("SELECT * FROM demo WHERE country = %(country)s", sql)
        self.assertEqual({"country": "BE"}, binds)

    def test_integer_value_binds_and_clamps_to_bounds(self):
        query = make_query(
            "SELECT * FROM demo LIMIT {{ limit }}",
            [
                {
                    "name": "limit",
                    "type": "integer",
                    "kind": "value",
                    "min": 1,
                    "max": 100,
                }
            ],
        )
        sql, binds = render_saved_query(query, {"limit": 5000})
        self.assertEqual("SELECT * FROM demo LIMIT %(limit)s", sql)
        self.assertEqual({"limit": 100}, binds)

        _, binds_low = render_saved_query(query, {"limit": -3})
        self.assertEqual({"limit": 1}, binds_low)

    def test_optional_filter_omitted_when_absent(self):
        query = make_query(
            "SELECT * FROM demo{% if country %} WHERE country = {{ country }}{% endif %}",
            [{"name": "country", "type": "string", "kind": "value"}],
        )
        sql, binds = render_saved_query(query, {})
        self.assertEqual("SELECT * FROM demo", sql)
        self.assertEqual({}, binds)

        sql_present, binds_present = render_saved_query(query, {"country": "BE"})
        self.assertEqual("SELECT * FROM demo WHERE country = %(country)s", sql_present)
        self.assertEqual({"country": "BE"}, binds_present)

    def test_default_is_used_when_param_absent(self):
        query = make_query(
            "SELECT * FROM demo LIMIT {{ limit }}",
            [
                {
                    "name": "limit",
                    "type": "integer",
                    "kind": "value",
                    "default": 10,
                }
            ],
        )
        _, binds = render_saved_query(query, {})
        self.assertEqual({"limit": 10}, binds)

    def test_enum_parameter_renders_allowlisted_token(self):
        query = make_query(
            "SELECT * FROM demo ORDER BY id {{ direction }}",
            [
                {
                    "name": "direction",
                    "type": "string",
                    "kind": "enum",
                    "choices": ["ASC", "DESC"],
                }
            ],
        )
        sql, binds = render_saved_query(query, {"direction": "DESC"})
        self.assertEqual("SELECT * FROM demo ORDER BY id DESC", sql)
        self.assertEqual({}, binds)

    def test_enum_parameter_rejects_value_outside_allowlist(self):
        query = make_query(
            "SELECT * FROM demo ORDER BY id {{ direction }}",
            [
                {
                    "name": "direction",
                    "type": "string",
                    "kind": "enum",
                    "choices": ["ASC", "DESC"],
                }
            ],
        )
        with self.assertRaises(ParameterError):
            render_saved_query(query, {"direction": "DESC; DROP TABLE demo"})

    def test_identifier_parameter_is_quoted_and_allowlisted(self):
        query = make_query(
            "SELECT * FROM demo ORDER BY {{ sort_column }}",
            [
                {
                    "name": "sort_column",
                    "type": "string",
                    "kind": "identifier",
                    "choices": ["id", "label"],
                }
            ],
        )
        sql, binds = render_saved_query(query, {"sort_column": "label"})
        self.assertEqual('SELECT * FROM demo ORDER BY "label"', sql)
        self.assertEqual({}, binds)

    def test_identifier_parameter_rejects_value_outside_allowlist(self):
        query = make_query(
            "SELECT * FROM demo ORDER BY {{ sort_column }}",
            [
                {
                    "name": "sort_column",
                    "type": "string",
                    "kind": "identifier",
                    "choices": ["id", "label"],
                }
            ],
        )
        with self.assertRaises(ParameterError):
            render_saved_query(query, {"sort_column": "id; DROP TABLE demo"})

    def test_unknown_parameter_is_rejected(self):
        query = make_query("SELECT 1", [])
        with self.assertRaises(ParameterError):
            render_saved_query(query, {"nope": "x"})

    def test_required_parameter_missing_is_rejected(self):
        query = make_query(
            "SELECT * FROM demo WHERE country = {{ country }}",
            [
                {
                    "name": "country",
                    "type": "string",
                    "kind": "value",
                    "required": True,
                }
            ],
        )
        with self.assertRaises(ParameterError):
            render_saved_query(query, {})

    def test_type_coercion_error_is_rejected(self):
        query = make_query(
            "SELECT * FROM demo LIMIT {{ limit }}",
            [{"name": "limit", "type": "integer", "kind": "value"}],
        )
        with self.assertRaises(ParameterError):
            render_saved_query(query, {"limit": "not-a-number"})

    def test_date_parameter_is_coerced_and_bound(self):
        query = make_query(
            "SELECT * FROM demo WHERE day = {{ day }}",
            [{"name": "day", "type": "date", "kind": "value"}],
        )
        sql, binds = render_saved_query(query, {"day": "2026-07-24"})
        self.assertEqual("SELECT * FROM demo WHERE day = %(day)s", sql)
        self.assertEqual({"day": datetime.date(2026, 7, 24)}, binds)


class RenderInjectionTest(SimpleTestCase):
    """A malicious caller value must always end up bound, never in the SQL text."""

    def test_string_injection_stays_bound(self):
        payload = "'; DROP TABLE users; --"
        query = make_query(
            "SELECT * FROM demo WHERE country = {{ country }}",
            [{"name": "country", "type": "string", "kind": "value"}],
        )
        sql, binds = render_saved_query(query, {"country": payload})

        self.assertEqual("SELECT * FROM demo WHERE country = %(country)s", sql)
        self.assertNotIn("DROP TABLE", sql)
        self.assertEqual({"country": payload}, binds)

    def test_boolean_style_injection_stays_bound(self):
        payload = "1 OR 1=1"
        query = make_query(
            "SELECT * FROM demo WHERE id = {{ id }}",
            [{"name": "id", "type": "string", "kind": "value"}],
        )
        sql, binds = render_saved_query(query, {"id": payload})

        self.assertEqual("SELECT * FROM demo WHERE id = %(id)s", sql)
        self.assertEqual({"id": payload}, binds)

    def test_quote_breaking_injection_stays_bound(self):
        payload = "x' OR '1'='1"
        query = make_query(
            "SELECT * FROM demo WHERE label = {{ label }}",
            [{"name": "label", "type": "string", "kind": "value"}],
        )
        sql, binds = render_saved_query(query, {"label": payload})

        self.assertNotIn("OR '1'='1", sql)
        self.assertEqual({"label": payload}, binds)


class RenderTemplateErrorTest(SimpleTestCase):
    def test_undeclared_reference_raises_render_error(self):
        query = make_query("SELECT * FROM demo WHERE x = {{ missing }}", [])
        with self.assertRaises(TemplateRenderError):
            render_saved_query(query, {})

    def test_sandbox_blocks_attribute_escape(self):
        query = make_query("SELECT {{ ''.__class__ }}", [])
        with self.assertRaises(TemplateRenderError):
            render_saved_query(query, {})

    def test_invalid_template_syntax_raises_render_error(self):
        query = make_query("SELECT {{ oops", [])
        with self.assertRaises(TemplateRenderError):
            render_saved_query(query, {})


class InvalidSpecTest(SimpleTestCase):
    def test_invalid_param_name_is_rejected(self):
        query = make_query(
            "SELECT 1",
            [{"name": "1bad", "type": "string", "kind": "value"}],
        )
        with self.assertRaises(ParameterError):
            render_saved_query(query, {})

    def test_enum_without_choices_is_rejected(self):
        query = make_query(
            "SELECT 1",
            [{"name": "direction", "type": "string", "kind": "enum"}],
        )
        with self.assertRaises(ParameterError):
            render_saved_query(query, {})

    def test_bounds_on_non_numeric_type_is_rejected(self):
        query = make_query(
            "SELECT 1",
            [{"name": "country", "type": "string", "kind": "value", "min": 1}],
        )
        with self.assertRaises(ParameterError):
            render_saved_query(query, {})
