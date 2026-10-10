"""pydantic-evals adapters over the deterministic verifiers.

The rules live in `evals.verifiers` as plain functions. These classes only
translate a report into the result types Logfire aggregates: bools as
pass-rates, floats as means, strings as distributions.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_evals.evaluators import (
    EvaluationReason,
    Evaluator,
    EvaluatorContext,
)

from ...fixtures import profile_spec
from ...verifiers import TIER_KEYS, run_verifiers
from ...verifiers.types import ASSERTION_TIERS
from .schemas import PipelineCreateInput, PipelineCreateMetadata, ProposedPipeline

Context = EvaluatorContext[
    PipelineCreateInput, ProposedPipeline, PipelineCreateMetadata
]


@dataclass
class VerifierScores(
    Evaluator[PipelineCreateInput, ProposedPipeline, PipelineCreateMetadata]
):
    """The deterministic tiers, as one score per tier plus the assertions.

    Returns a mapping rather than a single number, so a regression points at a
    tier. Counts ride along as each result's `reason`, which Logfire shows next
    to the value without making it a metric of its own.
    """

    def evaluate(self, ctx: Context) -> dict[str, EvaluationReason]:
        if not ctx.output.files:
            # No file set at all: the agent answered in prose, or the call was
            # rejected. Scoring the tiers on nothing would read as a clean pass,
            # and every assertion reports False rather than being omitted, so a
            # prose-only answer lowers the pass-rates instead of vanishing.
            reason = "no files proposed"
            failed: dict[str, EvaluationReason] = {
                f"{tier}_passed": EvaluationReason(value=False, reason=reason)
                for tier in ASSERTION_TIERS
            }
            for tier in TIER_KEYS:
                failed[f"{tier}_score"] = EvaluationReason(value=0.0, reason=reason)
            failed["average_score"] = EvaluationReason(value=0.0, reason=reason)
            return failed

        report = run_verifiers(
            ctx.output.files, profile_spec(ctx.inputs.fixture_profile)
        )
        return {
            name: EvaluationReason(value=metric.value, reason=metric.note or None)
            for name, metric in report.metrics().items()
        }


@dataclass
class Trajectory(
    Evaluator[PipelineCreateInput, ProposedPipeline, PipelineCreateMetadata]
):
    """What the agent did, rather than what it wrote.

    One assertion, because it changes how a failure reads: an agent that never
    called the tool failed differently from one whose call was rejected. The
    ordered tool list stays on the case output and in the trace, so further
    checks can be added without re-running anything.
    """

    def evaluate(self, ctx: Context) -> dict[str, EvaluationReason]:
        calls = ctx.output.tool_calls
        return {
            "proposed_a_pipeline": EvaluationReason(
                value="create_pipeline" in calls,
                reason=f"tools called: {', '.join(calls) if calls else 'none'}",
            )
        }
