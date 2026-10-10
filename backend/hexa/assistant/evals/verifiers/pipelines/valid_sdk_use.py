"""Tier 1: Check that the OpenHEXA SDK has been properly used by the generated code.

This verifier checks that every `openhexa.*` module and associated symbols
tbat the generated code uses exists and are not hallucinated.

"""

from __future__ import annotations

import ast

from ..common import symbols
from ..common.ast_utils import ParsedFile, attribute_chain
from ..types import Finding, TierResult

TIER = "valid_sdk_use"

# The SDK singletons, whose attribute surface is introspectable at runtime.
SINGLETON_ATTRS = {
    "workspace": symbols.workspace_attrs,
    "current_run": symbols.current_run_attrs,
}


def _check_imports(parsed: ParsedFile, findings: list[Finding]) -> int:
    checked = 0
    for node in ast.walk(parsed.tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if not module.startswith(symbols.OPENHEXA_ROOT):
                continue
            exists = symbols.module_exists(module)
            # None means the module is present but unimportable in this image;
            # it is skipped, so an unverifiable module neither helps nor hurts the score.
            if exists is None:
                continue
            if not exists:
                checked += 1
                findings.append(
                    Finding(
                        rule="unknown_module",
                        message=f"No module named {module!r} in the installed openhexa packages.",
                        file=parsed.name,
                        line=node.lineno,
                    )
                )
                continue
            for alias in node.names:
                has = symbols.module_has(module, alias.name)
                if has is None:
                    continue
                checked += 1
                if not has:
                    findings.append(
                        Finding(
                            rule="unknown_symbol",
                            message=f"{module}.{alias.name} does not exist.",
                            file=parsed.name,
                            line=node.lineno,
                        )
                    )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if not alias.name.startswith(symbols.OPENHEXA_ROOT):
                    continue
                exists = symbols.module_exists(alias.name)
                if exists is None:
                    continue
                checked += 1
                if not exists:
                    findings.append(
                        Finding(
                            rule="unknown_module",
                            message=f"No module named {alias.name!r}.",
                            file=parsed.name,
                            line=node.lineno,
                        )
                    )
    return checked


def _imported_singletons(tree: ast.Module) -> set[str]:
    """Names bound to `workspace` / `current_run` in this file.

    Only unaliased imports are tracked; an aliased singleton is skipped rather
    than guessed at, so the rule never reports a false hallucination.
    """
    bound: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not (node.module or "").startswith(
            symbols.OPENHEXA_ROOT
        ):
            continue
        for alias in node.names:
            if alias.name in SINGLETON_ATTRS and alias.asname is None:
                bound.add(alias.name)
    return bound


def _check_singleton_attrs(parsed: ParsedFile, findings: list[Finding]) -> int:
    bound = _imported_singletons(parsed.tree)
    checked = 0
    for node in ast.walk(parsed.tree):
        if not isinstance(node, ast.Attribute):
            continue
        chain = attribute_chain(node)
        if chain is None or len(chain) < 2:
            continue
        root, attr = chain[0], chain[1]
        if root not in bound:
            continue
        checked += 1
        known = SINGLETON_ATTRS[root]()
        if known and attr not in known:
            findings.append(
                Finding(
                    rule="unknown_attribute",
                    message=f"{root}.{attr} does not exist on the installed SDK.",
                    file=parsed.name,
                    line=node.lineno,
                )
            )
    return checked


def check_valid_sdk_use(parsed_files: list[ParsedFile]) -> TierResult:
    findings: list[Finding] = []
    checked = 0

    if not symbols.sdk_available():
        return TierResult(
            name=TIER,
            score=1.0,
            findings=[],
            counts={"sdk_symbols_checked": 0, "hallucinated_symbols": 0},
            note="openhexa-sdk is not installed; nothing could be checked",
        )

    for parsed in parsed_files:
        if parsed.tree is None:
            continue
        checked += _check_imports(parsed, findings)
        checked += _check_singleton_attrs(parsed, findings)

    score = 1.0 if checked == 0 else 1.0 - (len(findings) / checked)
    # The denominator is in the note on purpose: a 1.00 over zero checked
    # symbols means the code imported nothing from openhexa.*, not that it
    # used the SDK flawlessly.
    note = f"{len(findings)} hallucinated of {checked} symbol(s) checked"
    if findings:
        note += f" — {', '.join(sorted({f.message for f in findings})[:3])}"
    return TierResult(
        name=TIER,
        score=max(0.0, score),
        findings=findings,
        counts={"sdk_symbols_checked": checked, "hallucinated_symbols": len(findings)},
        note=note,
    )
