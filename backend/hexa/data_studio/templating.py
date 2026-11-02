"""SQL template rendering and parameter handling for saved queries.

Saved queries in the Data Studio can declare parameters (such as date ranges,
search terms, or category filters). This module parses and renders these query
templates using a sandboxed Jinja2 environment.

To prevent SQL injection, user-supplied parameter values are never interpolated
directly into SQL strings. Instead:
1. The template is rendered with unique placeholder tokens, and runtime values
   are extracted in order.
2. The database layer (`hexa.databases.query_text`) converts these tokens into
   driver-specific parameter placeholders (such as `%s` for psycopg2).
3. The database driver binds the values safely when the query executes.
"""

import re
import secrets
from dataclasses import dataclass
from datetime import date
from typing import Any

from jinja2 import (
    BaseLoader,
    StrictUndefined,
    TemplateError,
    Undefined,
    meta,
    pass_context,
)
from jinja2.sandbox import SandboxedEnvironment

PARAMETER_TYPES = ("STRING", "INTEGER", "FLOAT", "BOOLEAN", "DATE")

_PARAMETER_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class InvalidTemplateError(Exception):
    """Raised when query template syntax is invalid, uses unsupported tags, or references undeclared variables."""


class InvalidParametersError(Exception):
    """Raised when a parameter definition or supplied parameter value is invalid."""


class TemplateRenderError(Exception):
    """Raised when template rendering fails at runtime."""


@dataclass(frozen=True)
class RenderedQuery:
    """Represents a rendered query template before driver-specific placeholders are applied.

    Attributes
    ----------
        sql: The rendered SQL text containing placeholder tokens.
        params: Ordered list of parameter values corresponding to each token.
        token: The unique placeholder token string used in this render pass.
        values: Dictionary mapping parameter names to their resolved values.
    """

    sql: str
    params: list
    token: str
    values: dict


def build_environment(
    loader: BaseLoader | None = None, finalize=None
) -> SandboxedEnvironment:
    """Create a sandboxed Jinja environment for parsing and rendering SQL templates."""
    environment = SandboxedEnvironment(
        loader=loader,
        undefined=StrictUndefined,
        autoescape=False,
        finalize=finalize,
    )
    # Clear Jinja globals (like range, lipsum, dict) so they cannot be called
    # without being explicitly declared as parameters. This ensures template
    # validation can catch undeclared variables when queries are saved.
    environment.globals.clear()
    return environment


def _parse(content: str):
    """Parse SQL template content into a Jinja AST."""
    try:
        return build_environment().parse(content)
    except TemplateError as e:
        raise InvalidTemplateError(str(e)) from e


def collect_template_variables(content: str) -> set[str]:
    """Return the set of variable names referenced in the template."""
    return meta.find_undeclared_variables(_parse(content))


def _normalize_parameter(parameter: Any, seen: set[str]) -> dict:
    if not isinstance(parameter, dict):
        raise InvalidParametersError("Each parameter must be an object.")

    name = parameter.get("name")
    if not isinstance(name, str) or not _PARAMETER_NAME.match(name):
        raise InvalidParametersError(
            f"Invalid parameter name {name!r}: a name must start with a letter or an"
            " underscore and hold only letters, digits and underscores."
        )
    if name in seen:
        raise InvalidParametersError(f"Duplicate parameter name {name!r}.")

    parameter_type = parameter.get("type")
    if (
        not isinstance(parameter_type, str)
        or parameter_type.upper() not in PARAMETER_TYPES
    ):
        raise InvalidParametersError(
            f"Parameter {name!r} must have a type among {', '.join(PARAMETER_TYPES)}."
        )
    parameter_type = parameter_type.upper()

    multiple = _normalize_flag(name, "multiple", parameter.get("multiple"))
    required = _normalize_flag(name, "required", parameter.get("required"))

    help_text = parameter.get("help")
    if help_text is None:
        help_text = ""
    if not isinstance(help_text, str):
        raise InvalidParametersError(f"Parameter {name!r} has a non-string help text.")

    normalized = {
        "name": name,
        "type": parameter_type,
        "multiple": multiple,
        "required": required,
        "default": parameter.get("default"),
        "help": help_text,
    }
    if normalized["default"] is not None:
        # Validate default values on save so invalid defaults fail early.
        coerce_value(normalized, normalized["default"])

    return normalized


def _normalize_flag(name: str, key: str, value: Any) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise InvalidParametersError(f"Parameter {name!r} has a non-boolean {key!r}.")
    return value


def normalize_parameters(parameters: Any) -> list[dict]:
    """Validate a list of parameter declarations and populate default values for optional fields.

    Populates optional keys (multiple, required, default, help) so the stored
    dictionary matches the non-null fields required by the GraphQL schema.
    """
    if parameters is None:
        return []
    if not isinstance(parameters, list):
        raise InvalidParametersError("Parameters must be a list of parameter objects.")

    normalized = []
    seen: set[str] = set()
    for parameter in parameters:
        normalized.append(_normalize_parameter(parameter, seen))
        seen.add(normalized[-1]["name"])
    return normalized


def validate_saved_query_template(content: str, parameters: Any) -> list[dict]:
    """Validate template syntax and parameter declarations when saving a query.

    A query is a template only once it declares parameters; without any, its SQL is
    plain text that is never parsed, so braces in it (a nested array literal such as
    ``'{{1,2},{3,4}}'``) need no escaping. This mirrors ``render_saved_query``.
    Ensures the template syntax is valid, disallows unsupported tags ({% include %},
    {% import %}), and confirms all variables used in the SQL are declared.
    Returns the normalized parameter specifications.
    """
    normalized = normalize_parameters(parameters)
    if not normalized:
        return normalized
    ast = _parse(content)

    if next(iter(meta.find_referenced_templates(ast)), None) is not None:
        raise InvalidTemplateError(
            "{% include %} and {% import %} are not supported in saved queries."
        )

    declared = {parameter["name"] for parameter in normalized}
    undeclared = sorted(meta.find_undeclared_variables(ast) - declared)
    if undeclared:
        # All variables in the SQL must be declared as parameters.
        raise InvalidTemplateError(
            "The query uses undeclared parameters: " + ", ".join(undeclared) + "."
        )

    return normalized


def _coerce_scalar(name: str, parameter_type: str, value: Any):
    # Avoid echoing raw user input in error messages since it is logged to audit fields.
    invalid = InvalidParametersError(
        f"Parameter {name!r} expects a value of type {parameter_type}."
    )

    if parameter_type == "STRING":
        if not isinstance(value, str):
            raise invalid
        return value
    if parameter_type == "BOOLEAN":
        if not isinstance(value, bool):
            raise invalid
        return value
    if parameter_type == "INTEGER":
        # In Python, bool is a subclass of int, so exclude bool explicitly. Floats and numeric strings are also rejected.
        if isinstance(value, bool) or not isinstance(value, int):
            raise invalid
        return value
    if parameter_type == "FLOAT":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise invalid
        return float(value)
    if parameter_type == "DATE":
        if not isinstance(value, str):
            raise invalid
        try:
            # Parse ISO format (YYYY-MM-DD); psycopg2 natively adapts Python date objects.
            return date.fromisoformat(value)
        except ValueError:
            raise InvalidParametersError(
                f"Parameter {name!r} expects a date written as YYYY-MM-DD."
            ) from None

    raise InvalidParametersError(f"Parameter {name!r} has an unknown type.")


def coerce_value(parameter: dict, value: Any):
    """Validate and coerce a parameter value according to its declared specification."""
    name, parameter_type = parameter["name"], parameter["type"]

    if not parameter["multiple"]:
        return _coerce_scalar(name, parameter_type, value)

    # Scalar values must match the declared type; list wrapping is not inferred.
    if not isinstance(value, list):
        raise InvalidParametersError(
            f"Parameter {name!r} expects a list of {parameter_type} values."
        )
    # Empty lists are allowed and bind as empty arrays in PostgreSQL.
    return [_coerce_scalar(name, parameter_type, element) for element in value]


def bind_values(parameters: list[dict], values: Any) -> dict:
    """Validate and resolve runtime parameter values against declared specifications.

    Resolves default values for omitted optional parameters and raises
    InvalidParametersError for missing required parameters or unknown names.
    """
    if values is None:
        values = {}
    if not isinstance(values, dict):
        raise InvalidParametersError(
            "Parameters must be sent as a name → value object."
        )

    declared = {parameter["name"]: parameter for parameter in parameters}
    # Reject unrecognized parameter names to help callers catch typos.
    unknown = sorted(set(values) - set(declared))
    if unknown:
        raise InvalidParametersError(
            "Unknown parameters: " + ", ".join(repr(name) for name in unknown) + "."
        )

    bound = {}
    for name, parameter in declared.items():
        # Treat explicit None as omitted so default values can apply.
        value = values.get(name)
        if value is None:
            if parameter["default"] is not None:
                bound[name] = coerce_value(parameter, parameter["default"])
            elif parameter["required"]:
                raise InvalidParametersError(f"Parameter {name!r} is required.")
            else:
                bound[name] = None
        else:
            bound[name] = coerce_value(parameter, value)

    return bound


def render_saved_query(saved_query, values: Any = None) -> RenderedQuery:
    """Render a saved query template into SQL with placeholder tokens for parameter values.

    Returns the original SQL content unchanged if the query defines no parameters.
    The returned SQL uses neutral placeholder tokens, which are later converted to
    database-specific parameter markers.
    """
    parameters = normalize_parameters(saved_query.parameters)
    # Generate a unique token for this render pass to avoid accidental collisions with query text.
    token = f"__hexa_bind_{secrets.token_hex(16)}__"

    bound = bind_values(parameters, values)
    if not parameters:
        return RenderedQuery(saved_query.content, [], token, bound)

    params: list = []

    @pass_context
    def finalize(_context, value):
        # @pass_context prevents Jinja from pre-evaluating constant expressions at compile time,
        # ensuring parameter values stay in sync with placeholders.
        if isinstance(value, Undefined):
            # If Jinja encounters an Undefined variable or a sandbox security violation,
            # trigger its error immediately so it raises during template rendering.
            value._fail_with_undefined_error()
        params.append(value)
        return token

    # Rebuilding the environment per render keeps parameter collection thread-safe.
    environment = build_environment(finalize=finalize)
    try:
        sql = environment.from_string(saved_query.content).render(bound)
    except Exception as e:
        # Expressions run on caller-supplied values, so a template can raise
        # anything (a TypeError from {{ d + 1 }}, a ZeroDivisionError...), not
        # only Jinja's TemplateError. Every failure is reported and audited
        # the same way instead of surfacing as a raw Python error.
        raise TemplateRenderError(str(e)) from e

    if sql.count(token) != len(params):
        # Verify that each collected parameter has a corresponding placeholder in the rendered SQL,
        # guarding against constructs that capture output without emitting tokens.
        raise TemplateRenderError(
            "The query did not render one placeholder per value; it may use a construct"
            " that captures output, such as {% set %} ... {% endset %}."
        )

    return RenderedQuery(sql, params, token, bound)
