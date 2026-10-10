"""Tier 0: OpenHEXA's pipelines own admission check.

Runs `openhexa.sdk.pipelines.runtime.get_pipeline`, the same check we run
on pipeline push. It parses the AST without importing, so nothing in the proposed
files is executed. Anything it rejects would be rejected in production.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from openhexa.sdk.pipelines.exceptions import InvalidParameterError, PipelineNotFound
from openhexa.sdk.pipelines.runtime import get_pipeline

from ..common.ast_utils import PIPELINE_FILE
from ..types import Finding, Severity, TierResult

TIER = "valid_pipeline"


def check_valid_pipeline(files: dict[str, str]) -> TierResult:
    findings: list[Finding] = []

    if PIPELINE_FILE not in files:
        findings.append(
            Finding(
                rule="pipeline_file_missing",
                message=f"No {PIPELINE_FILE} at the root of the proposed file set.",
                file=PIPELINE_FILE,
            )
        )
        return TierResult(
            name=TIER,
            score=0.0,
            findings=findings,
            counts={"valid_pipeline_errors": 1},
            note=f"no {PIPELINE_FILE} in the proposed file set",
        )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, content in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        try:
            get_pipeline(root)
        except PipelineNotFound as exc:
            findings.append(
                Finding(
                    rule="pipeline_not_found",
                    message=f"No function decorated with @pipeline: {exc}",
                    file=PIPELINE_FILE,
                )
            )
        except InvalidParameterError as exc:
            findings.append(
                Finding(rule="invalid_parameter", message=str(exc), file=PIPELINE_FILE)
            )
        except SyntaxError as exc:
            findings.append(
                Finding(
                    rule="syntax_error",
                    message=f"{exc.msg}",
                    file=PIPELINE_FILE,
                    line=exc.lineno,
                )
            )
        except ValueError as exc:
            findings.append(
                Finding(
                    rule="invalid_decorator_argument",
                    message=str(exc),
                    file=PIPELINE_FILE,
                )
            )
        except Exception as exc:  # noqa: BLE001 - any rejection is a rejection
            findings.append(
                Finding(
                    rule="valid_pipeline_error",
                    message=f"{type(exc).__name__}: {exc}",
                    file=PIPELINE_FILE,
                    severity=Severity.ERROR,
                )
            )

    note = (
        "accepted by get_pipeline()"
        if not findings
        else f"{len(findings)} error(s): {', '.join(sorted({f.rule for f in findings}))}"
    )
    return TierResult(
        name=TIER,
        score=0.0 if findings else 1.0,
        findings=findings,
        counts={"valid_pipeline_errors": len(findings)},
        note=note,
    )
