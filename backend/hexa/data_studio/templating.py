"""Saved query templates enforce a strict trust boundary by separating SQL
structure from runtime values, binding inputs at execution rather than inlining them.

Trust Boundary & Data Flow:
* Trusted: Template SQL structure (written by workspace members).
* Untrusted: Parameter values (received from client-side JavaScript).

Pipeline Example:
  1. Raw        : SELECT * FROM t LIMIT {{ limit }}
  2. Render     : SELECT * FROM t LIMIT <TOKEN>      + values: [10]
  3. Convert    : SELECT * FROM t LIMIT %s           (via hexa.databases.query_text)
  4. Execute    : cursor.execute(sql, [10])          (psycopg2 binds safely)

Architecture & Security:
* Driver Isolation: Rendering stops at generic `<TOKEN>` placeholders. Translating
  tokens to driver syntax (e.g., `%s`) is handled exclusively by the `databases` layer.
* Zero Escape Hatches: No `sqlsafe` or `Markup` pass-throughs exist; untrusted values
  cannot reach the SQL grammar by design.

Error Handling (GraphQL Mapped):
* `InvalidTemplateError`: Bad template syntax, unsupported constructs, or undeclared variables.
* `InvalidParametersError`: Invalid parameter specs or caller value mismatches.
* `TemplateRenderError`: Internal render failures.
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
    """The template text cannot be used: syntax, unsupported construct, undeclared variable."""


class InvalidParametersError(Exception):
    """The parameter spec, or the values sent for it, are invalid."""


class TemplateRenderError(Exception):
    """Rendering a valid template failed (undefined value, sandbox refusal, ...)."""


@dataclass(frozen=True)
class RenderedQuery:
    """A rendered statement and its values, before any driver-specific placeholder.

    * `sql`: the statement, carrying `token` wherever a bound value belongs.
    * `params`: the bound values, in the order their tokens appear in `sql`.
    * `token`: the placeholder marker, regenerated on every render.
    * `values`: the same values keyed by parameter name, defaults resolved.
    """

    sql: str
    params: list
    token: str
    values: dict


def build_environment(
    loader: BaseLoader | None = None, finalize=None
) -> SandboxedEnvironment:
    """Build the sandboxed environment templates are parsed and rendered in.

    `loader` resolves {% include %} for a future snippets feature; nothing passes one today.
    """
    environment = SandboxedEnvironment(
        loader=loader,
        undefined=StrictUndefined,
        autoescape=False,
        finalize=finalize,
    )
    # Not about bounding work — the sandbox already swaps `range` for a capped
    # `safe_range`. It is about save-time validation: `meta.find_undeclared_variables`
    # skips any name present in `environment.globals`, so with them intact `{{ range(3) }}`
    # and `{{ lipsum() }}` would be invisible to the undeclared-variable check. Cleared,
    # they surface as undeclared and are rejected on save, which is what keeps "every
    # output node comes from a declared parameter" true.
    environment.globals.clear()
    return environment


def _parse(content: str):
    try:
        return build_environment().parse(content)
    except TemplateError as e:
        raise InvalidTemplateError(str(e)) from e


def collect_template_variables(content: str) -> set[str]:
    """Return the variable names the template expects to be passed in."""
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

    help_text = parameter.get("help") or ""
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
        # Validated here so a spec that could never bind is refused at save time; the raw
        # value is what gets stored, since a coerced DATE is not JSON-serialisable.
        coerce_value(normalized, normalized["default"])

    return normalized


def _normalize_flag(name: str, key: str, value: Any) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise InvalidParametersError(f"Parameter {name!r} has a non-boolean {key!r}.")
    return value


def normalize_parameters(parameters: Any) -> list[dict]:
    """Return the parameter spec with every optional key filled in, validating as it goes.

    GraphQL resolves these fields straight off the JSONField, where `multiple` and
    `required` are non-null, so a stored spec missing a key breaks every later read of the
    saved query.
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
    """Validate a template and its parameter spec at save time, returning the normalized spec.

    Checks that the spec is well formed, that the template uses no {% include %} or
    {% import %}, and that every variable it reads is declared. Sandbox refusals such as
    `{{ ''.__class__ }}` parse cleanly and only surface at render time.
    """
    normalized = normalize_parameters(parameters)
    ast = _parse(content)

    if next(iter(meta.find_referenced_templates(ast)), None) is not None:
        raise InvalidTemplateError(
            "{% include %} and {% import %} are not supported in saved queries."
        )

    declared = {parameter["name"] for parameter in normalized}
    undeclared = sorted(meta.find_undeclared_variables(ast) - declared)
    if undeclared:
        # What stops a template from silently executing a literal `{{ foo }}`. The reverse
        # (declared but unused) is allowed: the frontend form may want a parameter before
        # the SQL uses it.
        raise InvalidTemplateError(
            "The query uses undeclared parameters: " + ", ".join(undeclared) + "."
        )

    return normalized


def _coerce_scalar(name: str, parameter_type: str, value: Any):
    # Error messages name the parameter and the expected type and never echo the value:
    # it is attacker-controlled text that lands in an audit field people read.
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
        # `isinstance(True, int)` is True in Python, and every float is rejected — `10.0`
        # included, since a value written as a decimal is a caller who meant something
        # else. A numeric string is rejected too: guessing is how `LIMIT "10"` bugs happen.
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
            # psycopg2 adapts a `date` natively.
            return date.fromisoformat(value)
        except ValueError:
            raise InvalidParametersError(
                f"Parameter {name!r} expects a date written as YYYY-MM-DD."
            ) from None

    raise InvalidParametersError(f"Parameter {name!r} has an unknown type.")


def coerce_value(parameter: dict, value: Any):
    """Coerce one caller-supplied value against a normalized parameter spec."""
    name, parameter_type = parameter["name"], parameter["type"]

    if not parameter["multiple"]:
        return _coerce_scalar(name, parameter_type, value)

    # A bare scalar is rejected rather than wrapped, on the same "no guessing" grounds as
    # the numeric strings above. Nested arrays fall out of the element coercion.
    if not isinstance(value, list):
        raise InvalidParametersError(
            f"Parameter {name!r} expects a list of {parameter_type} values."
        )
    # An empty list is valid, and is the case this design is chosen for: it binds as an
    # empty PostgreSQL array, matching no rows under `= ANY` and every row under `<> ALL`,
    # with no syntax error either way.
    return [_coerce_scalar(name, parameter_type, element) for element in value]


def bind_values(parameters: list[dict], values: Any) -> dict:
    """Resolve the values a caller sent against the declared parameters.

    Unknown names are rejected. A missing or null value falls back to the parameter's
    default, then to `None` unless it is required.
    """
    if values is None:
        values = {}
    if not isinstance(values, dict):
        raise InvalidParametersError(
            "Parameters must be sent as a name → value object."
        )

    declared = {parameter["name"]: parameter for parameter in parameters}
    # Rejected rather than ignored: an unknown name is how a web app finds its typo.
    unknown = sorted(set(values) - set(declared))
    if unknown:
        raise InvalidParametersError(
            "Unknown parameters: " + ", ".join(repr(name) for name in unknown) + "."
        )

    bound = {}
    for name, parameter in declared.items():
        # An explicit null is treated as "not sent", the way an omitted GraphQL field is
        # everywhere else here.
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
    """Render a saved query into SQL carrying one token per bound value.

    A query declaring no parameters is returned byte-for-byte as stored; values sent for it
    are still checked. The returned `sql` holds `token`, not `%s`: converting it to a
    driver placeholder is `hexa.databases.query_text`'s job.
    """
    parameters = normalize_parameters(saved_query.parameters)
    # Word characters only, so the `%`-doubling done below the seam cannot touch it, and
    # freshly generated per render so it cannot be written literally into a template.
    token = f"__hexa_bind_{secrets.token_hex(16)}__"

    bound = bind_values(parameters, values)
    if not parameters:
        return RenderedQuery(saved_query.content, [], token, bound)

    params: list = []

    @pass_context
    def finalize(_context, value):
        # @pass_context stops Jinja constant-folding output nodes at compile time, which
        # would append literals to `params` out of order with their placeholders.
        if isinstance(value, Undefined):
            # Jinja passes the raw Undefined here before stringifying it, so returning a
            # token would skip the step that raises. Covers StrictUndefined and the
            # sandbox's refusals, which signal through an Undefined raising SecurityError.
            value._fail_with_undefined_error()
        params.append(value)
        return token

    # The environment is built per render because `params` is a per-call list closed over
    # by `finalize`. Compiling a short statement is cheap, and it keeps renders trivially
    # thread-safe.
    environment = build_environment(finalize=finalize)
    try:
        sql = environment.from_string(saved_query.content).render(bound)
    except TemplateError as e:
        # The common base of UndefinedError, TemplateSyntaxError and SecurityError.
        raise TemplateRenderError(str(e)) from e

    if sql.count(token) != len(params):
        # Jinja can bind a value without emitting a placeholder into the final text:
        # `{% set s %}{{ x }}{% endset %}` collects `x`, then re-binds the captured token
        # as a string when `{{ s }}` is output. Unchecked that reaches psycopg2 as "not
        # all arguments converted"; the check also guarantees a token can never travel
        # inside a bound value.
        raise TemplateRenderError(
            "The query did not render one placeholder per value; it may use a construct"
            " that captures output, such as {% set %} ... {% endset %}."
        )

    return RenderedQuery(sql, params, token, bound)
