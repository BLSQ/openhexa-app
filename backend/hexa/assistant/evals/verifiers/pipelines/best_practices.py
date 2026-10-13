"""Tier 3: Best practices checker for OpenHEXA pipelines.

This package checks several rules to evaluate if the generated pipeline is following "best practices".
This tier is the most opinionated of the suite, so we don't necesarily use it as an assertion in the evals
The score is the fraction of rules passed.
"""

from __future__ import annotations

import ast
import re

from ..common.ast_utils import (
    ParsedFile,
    called_attribute,
    called_name,
    string_constants,
)
from ..types import Finding, Severity, TierResult

TIER = "best_practices"

# Matched on request-issuing calls rather than imports: `urllib.parse.urlparse`
# is ordinary URL handling, and a `head()` connectivity probe has no toolbox
# equivalent. The rule targets hand-rolled API access, not any use of HTTP.
HTTP_CLIENTS = {"requests", "httpx", "aiohttp"}
HTTP_VERBS = {"get", "post", "put", "patch", "delete", "request"}
CONNECTION_TYPES = {"DHIS2Connection", "IASOConnection"}
CONNECTION_ACCESSORS = {"dhis2_connection", "iaso_connection"}
WRITE_METHODS = {
    "to_csv",
    "to_parquet",
    "to_excel",
    "to_file",
    "to_json",
    "write_text",
    "write_bytes",
    "savefig",
    "write_parquet",
    "write_csv",
}
# `add_file` covers publishing into a DatasetVersion, which is registration by
# another route. Over-matching here is deliberate: a missed warning costs less
# than condemning code that does publish its output.
OUTPUT_REGISTRARS = {"add_file_output", "add_database_output", "add_file"}

# Matched on the name a literal is bound to, never on the literal's shape.
# Entropy and length heuristics are unusable here: DHIS2 UIDs such as
# "HllvX50cXC0" look exactly like API keys, and real pipelines are full of them.
SECRET_NAMES = re.compile(
    r"(^|_)(password|passwd|pwd|secret|token|api_?key|access_?key|private_?key|"
    r"credential|credentials|bearer)($|_)",
    re.IGNORECASE,
)
# Literals that are self-evidently credentials whatever they are bound to.
CREDENTIAL_PREFIXES = (
    "sk-",
    "ghp_",
    "github_pat_",
    "xoxb-",
    "AKIA",
    "pylf_",
    "-----BEGIN",
)
# What workspace.files_path and workspace.tmp_path resolve to. Both can be
# overridden by WORKSPACE_FILES_PATH and WORKSPACE_TMP_PATH, which is why
# hardcoding them is suboptimal.
SDK_PATHS = ("/home/hexa/workspace", "/home/hexa/tmp")

RULES = (
    "no_hardcoded_secrets",
    "no_print",
    "use_toolbox_not_http",
    "no_env_credentials",
    "no_hardcoded_workspace_path",
    "register_outputs",
)


def _imported_modules(tree: ast.Module) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def _imported_names(tree: ast.Module) -> set[str]:
    return {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }


def _is_secret_name(name: str | None) -> bool:
    return bool(name) and bool(SECRET_NAMES.search(name))


def _secret_finding(file: str, node: ast.Constant, label: str) -> Finding:
    # The value is never echoed: findings travel into the metric note and on to
    # Logfire, and a proposed file set can carry a real key copied from context.
    return Finding(
        rule="no_hardcoded_secrets",
        message=(
            f"{label} is assigned a hardcoded {len(node.value)}-character literal. "
            "Read credentials from workspace.*_connection(), or take them as a "
            "@parameter(type=Secret)."
        ),
        file=file,
        line=node.lineno,
    )


def _check_hardcoded_secrets(parsed: ParsedFile, findings: list[Finding]) -> None:
    """Literals bound to a credential-shaped name, or with a known key prefix."""
    for node in ast.walk(parsed.tree):
        if isinstance(node, ast.Assign | ast.AnnAssign):
            value = node.value
            if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                name = getattr(target, "id", None) or getattr(target, "attr", None)
                if _is_secret_name(name) and value.value:
                    findings.append(_secret_finding(parsed.name, value, name))

        elif isinstance(node, ast.Call):
            for kw in node.keywords:
                value = kw.value
                if (
                    _is_secret_name(kw.arg)
                    and isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                    and value.value
                ):
                    findings.append(_secret_finding(parsed.name, value, kw.arg))

        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and _is_secret_name(key.value)
                    and isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                    and value.value
                ):
                    findings.append(_secret_finding(parsed.name, value, key.value))

    for const in string_constants(parsed.tree):
        if const.value.startswith(CREDENTIAL_PREFIXES):
            findings.append(_secret_finding(parsed.name, const, "a literal"))


def check_best_practices(parsed_files: list[ParsedFile]) -> TierResult:
    findings: list[Finding] = []
    trees = [p for p in parsed_files if p.tree is not None]

    http_calls: set[str] = set()
    touches_dhis2_or_iaso = False
    writes: list[tuple[str, int, str]] = []
    registers_output = False

    for parsed in trees:
        _check_hardcoded_secrets(parsed, findings)
        http_modules = _imported_modules(parsed.tree) & HTTP_CLIENTS
        if _imported_names(parsed.tree) & CONNECTION_TYPES:
            touches_dhis2_or_iaso = True

        for node in ast.walk(parsed.tree):
            if isinstance(node, ast.Call):
                if called_name(node) == "print":
                    findings.append(
                        Finding(
                            rule="no_print",
                            message="Use current_run.log_info() so the message reaches the run log.",
                            file=parsed.name,
                            line=node.lineno,
                            severity=Severity.WARNING,
                        )
                    )
                # Matched on the method name alone: an intermediate call such as
                # `pl.DataFrame().write_csv(...)` has no resolvable root, but the
                # method is still the signal.
                if isinstance(node.func, ast.Attribute):
                    method = node.func.attr
                    if method in CONNECTION_ACCESSORS:
                        touches_dhis2_or_iaso = True
                    if method in OUTPUT_REGISTRARS:
                        registers_output = True
                    if method in WRITE_METHODS:
                        writes.append((parsed.name, node.lineno, method))

                chain = called_attribute(node)
                if (
                    chain
                    and len(chain) == 2
                    and chain[0] in http_modules
                    and chain[1] in HTTP_VERBS
                ):
                    http_calls.add(f"{chain[0]}.{chain[1]}")
                if chain and chain[0] == "os" and chain[-1] in {"getenv", "environ"}:
                    findings.append(
                        Finding(
                            rule="no_env_credentials",
                            message=(
                                "Read credentials from workspace.*_connection() rather than the "
                                "environment."
                            ),
                            file=parsed.name,
                            line=node.lineno,
                            severity=Severity.WARNING,
                        )
                    )

            if isinstance(node, ast.Subscript):
                chain_target = getattr(node.value, "attr", None)
                root = getattr(getattr(node.value, "value", None), "id", None)
                if root == "os" and chain_target == "environ":
                    findings.append(
                        Finding(
                            rule="no_env_credentials",
                            message="Read credentials from workspace.*_connection(), not os.environ.",
                            file=parsed.name,
                            line=node.lineno,
                            severity=Severity.WARNING,
                        )
                    )

        for const in string_constants(parsed.tree):
            if const.value.startswith(SDK_PATHS):
                findings.append(
                    Finding(
                        rule="no_hardcoded_workspace_path",
                        message=(
                            f"Hardcoded path {const.value!r}; build paths from "
                            "workspace.files_path or workspace.tmp_path, which "
                            "honour the runtime override."
                        ),
                        file=parsed.name,
                        line=const.lineno,
                    )
                )

    if http_calls and touches_dhis2_or_iaso:
        findings.append(
            Finding(
                rule="use_toolbox_not_http",
                message=(
                    f"Calls DHIS2/IASO over {', '.join(sorted(http_calls))} instead of "
                    "openhexa.toolbox."
                ),
                file="pipeline.py",
            )
        )

    if writes and not registers_output:
        name, line, method = writes[0]
        findings.append(
            Finding(
                rule="register_outputs",
                message=(
                    f"Writes files ({method}) but never calls current_run.add_file_output() or "
                    "add_database_output(), so the outputs are invisible in the run."
                ),
                file=name,
                line=line,
                severity=Severity.WARNING,
            )
        )

    triggered = {f.rule for f in findings} & set(RULES)
    score = (len(RULES) - len(triggered)) / len(RULES)
    note = f"{len(triggered)} of {len(RULES)} rules triggered"
    if triggered:
        note += f": {', '.join(sorted(triggered))}"
    return TierResult(
        name=TIER,
        score=score,
        findings=findings,
        counts={"best_practices_rules_triggered": len(triggered)},
        note=note,
    )
