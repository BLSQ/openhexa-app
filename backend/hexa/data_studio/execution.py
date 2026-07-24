"""Rendering of parameterized (Jinja-templated) saved queries.

The author of a saved query is trusted, but the caller supplying parameter
values (a web app, or an anonymous visitor for a public query) is not. The
guiding rule is therefore:

    Caller values are always bound as database parameters, never rendered into
    the SQL text.

Jinja controls the *structure* of the query (which clauses appear); caller
values flow through psycopg2 server-side binding as ``%(name)s`` placeholders.
Parameters that cannot be bound (an ORDER BY column, a sort direction) are
restricted to an author-declared allowlist of choices.
"""

import datetime
import re

from jinja2 import StrictUndefined, TemplateError
from jinja2.sandbox import SandboxedEnvironment
from psycopg2 import Error as Psycopg2Error
from psycopg2.errors import QueryCanceled

from hexa.databases.utils import MultipleStatementsError, execute_database_query

PARAM_NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
ALLOWED_TYPES = {"string", "integer", "number", "boolean", "date"}
ALLOWED_KINDS = {"value", "enum", "identifier"}
NUMERIC_TYPES = {"integer", "number"}


class ParameterError(Exception):
    """Raised when the parameter spec or the caller-supplied values are invalid."""


class TemplateRenderError(Exception):
    """Raised when the saved query template fails to render."""


def validate_parameters_spec(spec_list: list) -> None:
    """Validate the shape of a saved query's declared parameter spec."""
    if not isinstance(spec_list, list):
        raise ParameterError("Parameters must be a list.")

    seen = set()
    for spec in spec_list:
        if not isinstance(spec, dict):
            raise ParameterError("Each parameter must be an object.")

        name = spec.get("name")
        if not isinstance(name, str) or not PARAM_NAME_RE.match(name):
            raise ParameterError(
                f"Invalid parameter name {name!r}: must match {PARAM_NAME_RE.pattern}."
            )
        if name in seen:
            raise ParameterError(f"Duplicate parameter name '{name}'.")
        seen.add(name)

        if spec.get("type") not in ALLOWED_TYPES:
            raise ParameterError(
                f"Parameter '{name}' has an invalid type; expected one of "
                f"{sorted(ALLOWED_TYPES)}."
            )

        kind = spec.get("kind", "value")
        if kind not in ALLOWED_KINDS:
            raise ParameterError(
                f"Parameter '{name}' has an invalid kind; expected one of "
                f"{sorted(ALLOWED_KINDS)}."
            )

        if kind in ("enum", "identifier"):
            choices = spec.get("choices")
            if not isinstance(choices, list) or not choices:
                raise ParameterError(
                    f"Parameter '{name}' of kind '{kind}' must declare a non-empty "
                    f"'choices' allowlist."
                )

        for bound in ("min", "max"):
            if spec.get(bound) is not None and spec["type"] not in NUMERIC_TYPES:
                raise ParameterError(
                    f"Parameter '{name}' may only set '{bound}' for numeric types."
                )


def _coerce(spec: dict, value):
    param_type = spec["type"]
    try:
        if param_type == "string":
            return str(value)
        if param_type == "integer":
            if isinstance(value, bool):
                raise ValueError
            return int(value)
        if param_type == "number":
            if isinstance(value, bool):
                raise ValueError
            return float(value)
        if param_type == "boolean":
            if isinstance(value, bool):
                return value
            normalized = str(value).strip().lower()
            if normalized in ("true", "1", "yes"):
                return True
            if normalized in ("false", "0", "no"):
                return False
            raise ValueError
        if param_type == "date":
            if isinstance(value, datetime.date):
                return value
            return datetime.date.fromisoformat(str(value))
    except (ValueError, TypeError):
        raise ParameterError(f"Parameter '{spec['name']}' is not a valid {param_type}.")
    raise ParameterError(f"Parameter '{spec['name']}' has unknown type '{param_type}'.")


def _apply_bounds(spec: dict, value):
    low, high = spec.get("min"), spec.get("max")
    if low is not None and value < low:
        value = low
    if high is not None and value > high:
        value = high
    return value


def _resolve_values(spec_list: list, caller_params: dict) -> dict:
    """Validate and coerce caller-supplied params against the declared spec."""
    by_name = {spec["name"]: spec for spec in spec_list}

    unknown = set(caller_params) - set(by_name)
    if unknown:
        raise ParameterError(f"Unknown parameter(s): {', '.join(sorted(unknown))}.")

    resolved = {}
    for name, spec in by_name.items():
        if caller_params.get(name) is not None:
            raw = caller_params[name]
        elif spec.get("default") is not None:
            raw = spec["default"]
        else:
            raw = None

        if raw is None:
            if spec.get("required"):
                raise ParameterError(f"Parameter '{name}' is required.")
            resolved[name] = None
            continue

        value = _coerce(spec, raw)
        if spec["type"] in NUMERIC_TYPES:
            value = _apply_bounds(spec, value)

        if spec.get("kind", "value") in ("enum", "identifier"):
            choices = [str(choice) for choice in spec["choices"]]
            if str(value) not in choices:
                raise ParameterError(
                    f"Parameter '{name}' must be one of: {', '.join(choices)}."
                )

        resolved[name] = value

    return resolved


def _quote_identifier(value: str) -> str:
    return '"' + str(value).replace('"', '""') + '"'


class _Binder:
    """Collects the values that will be bound by the driver."""

    def __init__(self):
        self.bind_params: dict = {}

    def placeholder(self, name: str, value) -> str:
        self.bind_params[name] = value
        return f"%({name})s"


class _Param:
    """A parameter exposed to the Jinja template.

    Rendering it (``{{ name }}``) emits a bound placeholder for value params, or
    a safe, allowlist-validated token for identifier/enum params. It never emits
    the raw caller value into the SQL text.
    """

    def __init__(self, spec: dict, value, binder: _Binder):
        self._name = spec["name"]
        self._kind = spec.get("kind", "value")
        self._value = value
        self._binder = binder

    def __str__(self) -> str:
        if self._kind == "value":
            return self._binder.placeholder(self._name, self._value)
        if self._value is None:
            raise ParameterError(
                f"Parameter '{self._name}' is required in this query but was "
                f"not provided."
            )
        if self._kind == "identifier":
            return _quote_identifier(self._value)
        return str(self._value)

    def __bool__(self) -> bool:
        return bool(self._value)

    def __eq__(self, other) -> bool:
        return self._value == other

    def __hash__(self) -> int:
        return hash(self._value)


def render_saved_query(saved_query, params: dict | None = None) -> tuple[str, dict]:
    """Render a saved query with the given parameters.

    Returns ``(sql_text, bind_params)`` ready to hand to
    ``execute_database_query``. Raises ``ParameterError`` for invalid parameters
    and ``TemplateRenderError`` for template failures (unknown references,
    sandbox violations, syntax errors).
    """
    params = params or {}
    spec_list = saved_query.parameters or []

    validate_parameters_spec(spec_list)
    resolved = _resolve_values(spec_list, params)

    binder = _Binder()
    context = {
        spec["name"]: _Param(spec, resolved[spec["name"]], binder) for spec in spec_list
    }

    env = SandboxedEnvironment(undefined=StrictUndefined, autoescape=False)
    try:
        template = env.from_string(saved_query.content)
        sql_text = template.render(context)
    except ParameterError:
        raise
    except TemplateError as e:
        raise TemplateRenderError(str(e))

    return sql_text, binder.bind_params


def execute_saved_query(
    saved_query, params: dict | None = None, max_rows: int | None = None
) -> dict:
    """Render and execute a saved query, returning a GraphQL-ready result dict.

    Shared by both the authenticated and the public (anonymous) execution paths;
    permission checks and query lookup are the caller's responsibility.
    """
    try:
        sql_text, bind_params = render_saved_query(saved_query, params)
    except ParameterError as e:
        return {
            "success": False,
            "errors": ["INVALID_PARAMETERS"],
            "error_message": str(e),
        }
    except TemplateRenderError as e:
        return {
            "success": False,
            "errors": ["TEMPLATE_ERROR"],
            "error_message": str(e),
        }

    max_rows_kwarg = {} if max_rows is None else {"max_rows": max_rows}
    try:
        result = execute_database_query(
            saved_query.workspace, sql_text, bind_params=bind_params, **max_rows_kwarg
        )
    except MultipleStatementsError as e:
        return {
            "success": False,
            "errors": ["MULTIPLE_STATEMENTS"],
            "error_message": str(e),
        }
    except QueryCanceled as e:
        return {
            "success": False,
            "errors": ["QUERY_TIMEOUT"],
            "error_message": str(e).strip(),
        }
    except Psycopg2Error as e:
        return {
            "success": False,
            "errors": ["QUERY_ERROR"],
            "error_message": str(e).strip(),
        }
    return {"success": True, "errors": [], **result}
