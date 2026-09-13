"""Suite registry, the unit of extension.

A suite bundles one hosted dataset, one task callable, one evaluator set and the
types they share. Adding the edit, webapp or SQL agents means adding a suite
here. `evals.core` does not change.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic_evals.evaluators import Evaluator

from hexa.assistant.instructions import InstructionSet

from .pipeline_create import evaluators as create_evaluators
from .pipeline_create import task as create_task
from .pipeline_create.schemas import (
    PipelineCreateInput,
    PipelineCreateMetadata,
    ProposedPipeline,
)


@dataclass(frozen=True)
class SuiteSpec:
    name: str
    dataset_name: str
    input_type: type[Any]
    output_type: type[Any]
    metadata_type: type[Any]
    instruction_set: InstructionSet
    evaluators: tuple[Evaluator, ...]
    make_task: Callable[[], Callable]


PIPELINE_CREATE = SuiteSpec(
    name="pipeline_create",
    dataset_name="create-pipeline-outcome-evals",
    input_type=PipelineCreateInput,
    output_type=ProposedPipeline,
    metadata_type=PipelineCreateMetadata,
    instruction_set=InstructionSet.CREATE_PIPELINE,
    evaluators=(create_evaluators.VerifierScores(), create_evaluators.Trajectory()),
    make_task=create_task.make_task,
)

SUITES: dict[str, SuiteSpec] = {PIPELINE_CREATE.name: PIPELINE_CREATE}


def get_suite(name: str) -> SuiteSpec:
    if name not in SUITES:
        raise KeyError(
            f"Unknown suite {name!r}. Known suites: {', '.join(sorted(SUITES))}."
        )
    return SUITES[name]
