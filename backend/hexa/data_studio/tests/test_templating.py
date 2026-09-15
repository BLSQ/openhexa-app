from datetime import date

from django.test import SimpleTestCase

from hexa.data_studio.templating import (
    InvalidParametersError,
    InvalidTemplateError,
    TemplateRenderError,
    bind_values,
    build_environment,
    coerce_value,
    collect_template_variables,
    normalize_parameters,
    render_saved_query,
    validate_saved_query_template,
)
from hexa.databases.query_text import to_psycopg2


class FakeSavedQuery:
    """Stands in for the model: rendering only ever reads these two attributes."""

    def __init__(self, content, parameters=None):
        self.content = content
        self.parameters = parameters or []


def parameter(name, parameter_type="STRING", **kwargs):
    return {"name": name, "type": parameter_type, **kwargs}


def render(content, parameters=None, values=None):
    return render_saved_query(FakeSavedQuery(content, parameters), values)


class RenderTest(SimpleTestCase):
    def test_binds_a_value_instead_of_inlining_it(self):
        rendered = render(
            "SELECT * FROM t LIMIT {{ limit }}",
            [parameter("limit", "INTEGER")],
            {"limit": 10},
        )
        sql, params = to_psycopg2(rendered)
        self.assertEqual("SELECT * FROM t LIMIT %s", sql)
        self.assertEqual([10], params)

    def test_a_query_without_parameters_is_returned_byte_for_byte(self):
        content = "SELECT * FROM t WHERE name LIKE '%foo%'"
        rendered = render(content)
        self.assertEqual(content, rendered.sql)
        self.assertEqual([], rendered.params)
        # None, not [], or psycopg2 would %-format a statement it has no values for.
        self.assertEqual((content, None), to_psycopg2(rendered))

    def test_injection_arrives_as_a_value_not_as_sql(self):
        rendered = render(
            "SELECT * FROM t WHERE name = {{ name }}",
            [parameter("name")],
            {"name": "1; DROP TABLE users"},
        )
        self.assertNotIn("DROP TABLE", rendered.sql)
        self.assertEqual(["1; DROP TABLE users"], rendered.params)
        sql, params = to_psycopg2(rendered)
        self.assertEqual(1, sql.count("%s"))
        self.assertNotIn("DROP TABLE", sql)

    def test_rendering_stops_at_the_token(self):
        """The seam: `to_psycopg2` is the only thing that may write a psycopg2 placeholder."""
        rendered = render("SELECT {{ a }}", [parameter("a", "INTEGER")], {"a": 1})
        self.assertIn(rendered.token, rendered.sql)
        self.assertNotIn("%s", rendered.sql)
        self.assertIn("%s", to_psycopg2(rendered)[0])

    def test_a_literal_percent_survives_the_conversion(self):
        rendered = render(
            "SELECT * FROM t WHERE name LIKE '%foo%' AND id = {{ id }}",
            [parameter("id", "INTEGER")],
            {"id": 7},
        )
        sql, params = to_psycopg2(rendered)
        # Doubled for psycopg2, which un-doubles it as it binds; the placeholder
        # written by the same pass must not itself be doubled.
        self.assertEqual("SELECT * FROM t WHERE name LIKE '%%foo%%' AND id = %s", sql)
        self.assertEqual(1, sql.count("%s"))
        self.assertEqual([7], params)

    def test_placeholder_order_matches_value_order(self):
        """The regression `@pass_context` on `finalize` exists to prevent."""
        rendered = render(
            "A {{ a }} B {{ 'LIT' }} C {{ a }} D {% for n in ns %}{{ n }},{% endfor %} E {{ b }}",
            [
                parameter("a", "INTEGER"),
                parameter("b", "INTEGER"),
                parameter("ns", "INTEGER", multiple=True),
            ],
            {"a": 1, "b": 2, "ns": [7, 8]},
        )
        self.assertEqual([1, "LIT", 1, 7, 8, 2], rendered.params)
        self.assertEqual(6, rendered.sql.count(rendered.token))

    def test_control_flow_sees_the_real_typed_value(self):
        for limit, expected in ((50, "BIG"), (1, "SMALL")):
            with self.subTest(limit=limit):
                rendered = render(
                    "{% if limit > 10 %}BIG{% else %}SMALL{% endif %} {{ limit }}",
                    [parameter("limit", "INTEGER")],
                    {"limit": limit},
                )
                self.assertTrue(rendered.sql.startswith(expected))
                self.assertEqual([limit], rendered.params)

    def test_a_safe_filtered_value_is_still_bound(self):
        """`| safe` hands `finalize` a Markup; there is no pass-through for it."""
        rendered = render("SELECT {{ x | safe }}", [parameter("x")], {"x": "<b>"})
        self.assertEqual(rendered.token, rendered.sql.replace("SELECT ", ""))
        self.assertEqual(["<b>"], rendered.params)

    def test_values_are_exposed_by_name_with_defaults_resolved(self):
        rendered = render(
            "SELECT {{ a }}",
            [parameter("a", "INTEGER", default=5), parameter("b", "STRING")],
            {},
        )
        self.assertEqual({"a": 5, "b": None}, rendered.values)


class RenderFailureTest(SimpleTestCase):
    def test_the_sandbox_and_undefined_surface_as_a_render_error(self):
        """Without the `Undefined` guard in `finalize` these render "successfully".

        Jinja hands `finalize` the raw `Undefined` before anything stringifies it, so a
        hook that returns a token short-circuits the only step that would have raised;
        the failure would then surface from psycopg2 as "can't adapt type
        'StrictUndefined'". Each of these must fail here instead.
        """
        for content in (
            "SELECT {{ ''.__class__ }}",
            "SELECT {{ x.__class__ }}",
            "SELECT {{ x.foo }}",
            "SELECT {{ x.__init__ }}",
            "SELECT {{ undeclared }}",
        ):
            with self.subTest(content=content):
                with self.assertRaises(TemplateRenderError):
                    render(content, [parameter("x")], {"x": "hi"})

    def test_a_construct_that_captures_output_is_refused(self):
        """`{% set %}...{% endset %}` binds a value without emitting a placeholder."""
        with self.assertRaises(TemplateRenderError):
            render(
                "{% set s %}{{ x }}{% endset %}SELECT {{ s }}",
                [parameter("x")],
                {"x": "v"},
            )


class EnvironmentTest(SimpleTestCase):
    def test_globals_are_cleared_so_they_cannot_hide_from_validation(self):
        self.assertEqual({}, dict(build_environment().globals))

    def test_there_is_no_sqlsafe_filter(self):
        self.assertNotIn("sqlsafe", build_environment().filters)

    def test_a_global_is_rejected_on_save_as_an_undeclared_variable(self):
        for content in (
            "{{ range(3) }}",
            "{{ lipsum() }}",
            "{% set n = namespace() %}",
        ):
            with self.subTest(content=content):
                with self.assertRaises(InvalidTemplateError):
                    validate_saved_query_template(content, [])

    def test_collect_template_variables(self):
        self.assertEqual(
            {"a", "b"}, collect_template_variables("{{ a }}{% if b %}x{% endif %}")
        )


class CoercionTest(SimpleTestCase):
    def coerce(self, parameter_type, value, **kwargs):
        spec = normalize_parameters([parameter("p", parameter_type, **kwargs)])[0]
        return coerce_value(spec, value)

    def test_accepted_values(self):
        self.assertEqual(10, self.coerce("INTEGER", 10))
        self.assertEqual(10.0, self.coerce("FLOAT", 10))
        self.assertEqual(10.5, self.coerce("FLOAT", 10.5))
        self.assertEqual("x", self.coerce("STRING", "x"))
        self.assertIs(True, self.coerce("BOOLEAN", True))
        self.assertEqual(date(2026, 1, 1), self.coerce("DATE", "2026-01-01"))

    def test_rejected_values(self):
        # `isinstance(True, int)` is True in Python, so both numeric types must
        # exclude bool explicitly; a numeric string is how `LIMIT "10"` bugs happen;
        # and a decimal written for an INTEGER is a caller who meant something else.
        for parameter_type, value in (
            ("INTEGER", True),
            ("FLOAT", True),
            ("INTEGER", 10.5),
            ("INTEGER", 10.0),
            ("INTEGER", "10"),
            ("FLOAT", "10"),
            ("BOOLEAN", 1),
            ("STRING", 5),
            ("DATE", "01/01/2026"),
            ("DATE", 20260101),
        ):
            with self.subTest(type=parameter_type, value=value):
                with self.assertRaises(InvalidParametersError):
                    self.coerce(parameter_type, value)

    def test_an_error_message_never_echoes_the_rejected_value(self):
        """It is attacker-controlled text landing in an audit field people read."""
        with self.assertRaises(InvalidParametersError) as raised:
            self.coerce("INTEGER", "<script>alert(1)</script>")
        self.assertNotIn("script", str(raised.exception))

    def test_multiple_binds_one_list_value(self):
        self.assertEqual([1, 2], self.coerce("INTEGER", [1, 2], multiple=True))

    def test_multiple_accepts_an_empty_list(self):
        """The case the design is chosen for: no rows under `= ANY`, all under `<> ALL`."""
        self.assertEqual([], self.coerce("INTEGER", [], multiple=True))

    def test_multiple_rejects_a_scalar_a_nested_list_and_bad_elements(self):
        for value in (1, "a", [[1]], ["1"]):
            with self.subTest(value=value):
                with self.assertRaises(InvalidParametersError):
                    self.coerce("INTEGER", value, multiple=True)

    def test_a_list_binds_as_a_single_placeholder(self):
        rendered = render(
            "SELECT * FROM t WHERE d = ANY({{ ds }})",
            [parameter("ds", multiple=True)],
            {"ds": ["a", "b"]},
        )
        sql, params = to_psycopg2(rendered)
        self.assertEqual(1, sql.count("%s"))
        self.assertEqual([["a", "b"]], params)


class BindValuesTest(SimpleTestCase):
    SPEC = [
        {"name": "a", "type": "INTEGER", "required": True},
        {"name": "b", "type": "DATE", "default": "2026-01-01"},
        {"name": "c", "type": "STRING"},
    ]

    def bind(self, values):
        return bind_values(normalize_parameters(self.SPEC), values)

    def test_resolves_defaults_and_missing_optionals(self):
        self.assertEqual(
            {"a": 1, "b": date(2026, 1, 1), "c": None}, self.bind({"a": 1})
        )

    def test_an_explicit_null_is_treated_as_not_sent(self):
        self.assertEqual(date(2026, 1, 1), self.bind({"a": 1, "b": None})["b"])

    def test_a_missing_required_value_is_rejected(self):
        with self.assertRaises(InvalidParametersError):
            self.bind({})

    def test_an_unknown_name_is_rejected_rather_than_ignored(self):
        """How a web app finds its typo."""
        with self.assertRaises(InvalidParametersError) as raised:
            self.bind({"a": 1, "limitt": 2})
        self.assertIn("limitt", str(raised.exception))

    def test_values_must_be_an_object(self):
        with self.assertRaises(InvalidParametersError):
            self.bind(["a", 1])


class ValidateOnSaveTest(SimpleTestCase):
    def test_returns_a_normalized_spec(self):
        self.assertEqual(
            [
                {
                    "name": "a",
                    "type": "INTEGER",
                    "multiple": False,
                    "required": False,
                    "default": None,
                    "help": "",
                }
            ],
            validate_saved_query_template(
                "SELECT {{ a }}", [{"name": "a", "type": "integer"}]
            ),
        )

    def test_a_declared_but_unused_parameter_is_allowed(self):
        # The frontend form may want a parameter before the SQL uses it.
        self.assertEqual(
            1, len(validate_saved_query_template("SELECT 1", [parameter("a")]))
        )

    def test_rejected_templates(self):
        for label, content, parameters in (
            ("undeclared variable", "SELECT {{ foo }}", []),
            ("syntax error", "SELECT {{ foo ", []),
            ("include", "{% include 'x' %}", []),
            ("import", "{% import 'm' as m %}", []),
        ):
            with self.subTest(label):
                with self.assertRaises(InvalidTemplateError):
                    validate_saved_query_template(content, parameters)

    def test_rejected_specs(self):
        for label, parameters in (
            ("duplicate name", [parameter("a"), parameter("a", "INTEGER")]),
            ("bad name", [parameter("1a")]),
            ("unknown type", [parameter("a", "DECIMAL")]),
            ("missing type", [{"name": "a"}]),
            ("bad default", [parameter("a", "INTEGER", default="x")]),
            ("non-boolean multiple", [parameter("a", multiple="yes")]),
            ("not an object", ["a"]),
            ("not a list", {"a": 1}),
        ):
            with self.subTest(label):
                with self.assertRaises(InvalidParametersError):
                    validate_saved_query_template("SELECT 1", parameters)

    def test_a_multiple_default_must_be_a_list(self):
        with self.assertRaises(InvalidParametersError):
            validate_saved_query_template(
                "SELECT 1", [parameter("a", "INTEGER", multiple=True, default=1)]
            )
