"""Shared types for the verifiers.

This package imports nothing from Django or pydantic-evals, so the rules can be
tested without a runner or a database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


# Tiers that also emit a boolean `<tier>_passed`, which Logfire aggregates as a
# pass-rate. `best_practices` is excluded: most of its findings are warnings, so
# a pass there would hide them.
ASSERTION_TIERS = ("valid_pipeline", "valid_sdk_use", "grounding")


@dataclass(frozen=True)
class Finding:
    rule: str
    message: str
    file: str
    line: int | None = None
    severity: Severity = Severity.ERROR


@dataclass(frozen=True)
class Metric:
    """One reported number plus a note explaining it.

    Counts such as `sdk_symbols_checked` ride in the note instead of becoming
    metrics of their own, so the reported surface stays small without losing
    the denominator.
    """

    value: bool | float
    note: str = ""


@dataclass
class TierResult:
    name: str
    score: float
    findings: list[Finding] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    note: str = ""

    @property
    def passed(self) -> bool:
        return not any(f.severity is Severity.ERROR for f in self.findings)


@dataclass(frozen=True)
class WorldSpec:
    """The seeded eval workspace, as far as a verifier needs to know it.

    A value object rather than the Django models, so grounding rules can be
    tested without a database.
    """

    connection_slugs: frozenset[str] = frozenset()
    dataset_slugs: frozenset[str] = frozenset()
    file_paths: frozenset[str] = frozenset()

    @classmethod
    def empty(cls) -> WorldSpec:
        return cls()


@dataclass
class VerifierReport:
    tiers: dict[str, TierResult] = field(default_factory=dict)

    @property
    def findings(self) -> list[Finding]:
        return [f for tier in self.tiers.values() for f in tier.findings]

    @property
    def average_score(self) -> float:
        """Mean of the tier scores.

        Always reported alongside the per-tier scores. A blended number alone
        does not say which tier moved.
        """
        if not self.tiers:
            return 1.0
        return sum(t.score for t in self.tiers.values()) / len(self.tiers)

    def metrics(self) -> dict[str, Metric]:
        """One score per tier, plus the assertions.

        Counts ride in each Metric's note rather than becoming metrics of their
        own.
        """
        out: dict[str, Metric] = {}
        for key, tier in self.tiers.items():
            out[f"{key}_score"] = Metric(tier.score, tier.note)
        for key in ASSERTION_TIERS:
            tier = self.tiers.get(key)
            out[f"{key}_passed"] = Metric(
                tier.passed if tier else True, tier.note if tier else ""
            )
        out["average_score"] = Metric(
            self.average_score, f"mean of {len(self.tiers)} tier scores"
        )
        return out
