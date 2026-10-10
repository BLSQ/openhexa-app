"""Deterministic scoring of what an agent produced.

`run_verifiers` scores a proposed pipeline across four tiers. Tiers 0-2 check
against something outside this code: the SDK's own validator, the installed
packages, and the seeded workspace. Tier 3 is a set of style best practices,
so it is never combined with the others.

The rules are plain functions of (files, world). They import nothing from
Django or pydantic-evals, so they can be tested without a runner or a database.
"""

from __future__ import annotations

from .common.ast_utils import parse_files
from .pipelines.best_practices import check_best_practices
from .pipelines.grounding import check_grounding
from .pipelines.valid_pipeline import check_valid_pipeline
from .pipelines.valid_sdk_use import check_valid_sdk_use
from .types import (
    ASSERTION_TIERS,
    Finding,
    Severity,
    TierResult,
    VerifierReport,
    WorldSpec,
)

__all__ = [
    "ASSERTION_TIERS",
    "TIER_KEYS",
    "Finding",
    "Severity",
    "TierResult",
    "VerifierReport",
    "WorldSpec",
    "check_valid_pipeline",
    "check_grounding",
    "check_best_practices",
    "check_valid_sdk_use",
    "run_verifiers",
]


TIER_KEYS = ("valid_pipeline", "valid_sdk_use", "grounding", "best_practices")


def run_verifiers(
    files: dict[str, str], world: WorldSpec | None = None
) -> VerifierReport:
    """Score a proposed pipeline file set across tiers 0-3."""
    world = world or WorldSpec.empty()
    parsed_files = parse_files(files)
    return VerifierReport(
        tiers={
            "valid_pipeline": check_valid_pipeline(files),
            "valid_sdk_use": check_valid_sdk_use(parsed_files),
            "grounding": check_grounding(parsed_files, world),
            "best_practices": check_best_practices(parsed_files),
        }
    )
