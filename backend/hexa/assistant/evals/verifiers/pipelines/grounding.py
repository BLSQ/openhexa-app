"""Tier 2: Identifiers in the code must exist in the workspace.

A static check against a description of the seeded world workspace and some of its contents.
It catches a well-formed call to a hallucinated connection, dataset or file.
"""

from __future__ import annotations

from ..common.ast_utils import (
    ParsedFile,
    called_attribute,
    first_string_arg,
    iter_calls,
)
from ..types import Finding, TierResult, WorldSpec

TIER = "grounding"

CONNECTION_METHODS = {
    "dhis2_connection",
    "iaso_connection",
    "postgresql_connection",
    "s3_connection",
    "gcs_connection",
    "custom_connection",
    "get_connection",
}
DATASET_METHODS = {"get_dataset"}
FILE_METHODS = {"get_file"}


def _known(method: str, world: WorldSpec) -> tuple[frozenset[str], str]:
    if method in CONNECTION_METHODS:
        return world.connection_slugs, "connection"
    if method in DATASET_METHODS:
        return world.dataset_slugs, "dataset"
    return world.file_paths, "file"


def check_grounding(parsed_files: list[ParsedFile], world: WorldSpec) -> TierResult:
    findings: list[Finding] = []
    checked = 0

    for parsed in parsed_files:
        if parsed.tree is None:
            continue
        for call in iter_calls(parsed.tree):
            chain = called_attribute(call)
            if chain is None or len(chain) < 2:
                continue
            method = chain[-1]
            if method not in CONNECTION_METHODS | DATASET_METHODS | FILE_METHODS:
                continue
            # A non-literal argument comes from a pipeline parameter, which is
            # the idiomatic form and cannot be resolved statically.
            literal = first_string_arg(call) or first_string_arg(call, "identifier")
            if literal is None:
                continue
            checked += 1
            known, kind = _known(method, world)
            if literal.value not in known:
                findings.append(
                    Finding(
                        rule=f"unknown_{kind}",
                        message=(
                            f"{method}({literal.value!r}) — no such {kind} in the eval workspace. "
                            f"Known: {', '.join(sorted(known)) or 'none'}."
                        ),
                        file=parsed.name,
                        line=literal.lineno,
                    )
                )

    score = 1.0 if checked == 0 else 1.0 - (len(findings) / checked)
    note = f"{len(findings)} ungrounded of {checked} literal reference(s) checked"
    if checked == 0:
        note += " — identifiers came from parameters, or none were used"
    return TierResult(
        name=TIER,
        score=max(0.0, score),
        findings=findings,
        counts={
            "grounded_references_checked": checked,
            "ungrounded_references": len(findings),
        },
        note=note,
    )
