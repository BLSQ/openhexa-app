"""Scores for a proposed web app version, against the seeded files it started from."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext

from ...fixtures import webapp_files
from .schemas import ProposedWebappVersion, WebappEditInput, WebappEditMetadata

Context = EvaluatorContext[WebappEditInput, ProposedWebappVersion, WebappEditMetadata]


@dataclass
class ProposalChecks(
    Evaluator[WebappEditInput, ProposedWebappVersion, WebappEditMetadata]
):
    """Did the requested change land, and only that change.

    `first_proposal_accepted` is the one aimed at the reading tools: a rejected
    proposal usually means a patch whose old_string did not match the file, for
    instance one copied with line-number prefixes.
    """

    def evaluate(self, ctx: Context) -> dict[str, EvaluationReason]:
        output = ctx.output
        first_ok = EvaluationReason(
            value=output.rejected_proposals == 0,
            reason=f"{output.rejected_proposals} rejected proposal(s)",
        )
        if output.files is None:
            reason = "no version proposed"
            return {
                "proposed_a_version": EvaluationReason(value=False, reason=reason),
                "change_landed": EvaluationReason(value=False, reason=reason),
                "others_preserved": EvaluationReason(value=False, reason=reason),
                "first_proposal_accepted": first_ok,
                "checks_score": EvaluationReason(value=0.0, reason=reason),
            }

        checks = ctx.metadata.checks
        failures = [
            failure
            for check in checks
            for failure in check.failures(output.files.get(check.path))
        ]
        passed = sum(
            not check.failures(output.files.get(check.path)) for check in checks
        )

        original = webapp_files(ctx.inputs.webapp)
        allowed = {check.path for check in checks} | set(ctx.metadata.may_change)
        changed = {
            path for path in original if output.files.get(path) != original[path]
        } | (set(output.files) - set(original))
        unexpected = sorted(changed - allowed)

        return {
            "proposed_a_version": EvaluationReason(value=True),
            "change_landed": EvaluationReason(
                value=not failures, reason="; ".join(failures) or None
            ),
            "others_preserved": EvaluationReason(
                value=not unexpected,
                reason=f"also changed: {', '.join(unexpected)}" if unexpected else None,
            ),
            "first_proposal_accepted": first_ok,
            "checks_score": EvaluationReason(
                value=passed / len(checks) if checks else 1.0
            ),
        }
