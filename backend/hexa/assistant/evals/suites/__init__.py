"""Suite registry, the unit of extension.

A suite bundles one cases file, one task callable, one evaluator set and the
types they share. Adding the edit, webapp or SQL agents means adding a suite
here. `evals.core` does not change.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic_evals.evaluators import Evaluator

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.agents.edit_webapp_agent import EditWebappAgent

from .pipeline_create import evaluators as create_evaluators
from .pipeline_create import task as create_task
from .pipeline_create.schemas import (
    PipelineCreateInput,
    PipelineCreateMetadata,
    ProposedPipeline,
)
from .webapp_edit import evaluators as webapp_edit_evaluators
from .webapp_edit import task as webapp_edit_task
from .webapp_edit.schemas import (
    ProposedWebappVersion,
    WebappEditInput,
    WebappEditMetadata,
)


@dataclass(frozen=True)
class SuiteSpec:
    name: str
    cases_path: Path
    input_type: type[Any]
    output_type: type[Any]
    metadata_type: type[Any]
    # The agent under test. Its agent_key decides the model it runs on, and its
    # instruction_set the prompt that instructions_hash fingerprints.
    agent: type[BaseAgent]
    evaluators: tuple[Evaluator, ...]
    make_task: Callable[[], Callable]
    # Entered around the whole evaluation, inside the test environment, for a
    # suite that needs a service the test environment stubs out.
    environment: Callable[[], AbstractContextManager] = nullcontext


PIPELINE_CREATE = SuiteSpec(
    name="pipeline_create",
    cases_path=Path(__file__).parent / "pipeline_create" / "cases.yaml",
    input_type=PipelineCreateInput,
    output_type=ProposedPipeline,
    metadata_type=PipelineCreateMetadata,
    agent=CreatePipelineAgent,
    evaluators=(create_evaluators.VerifierScores(), create_evaluators.Trajectory()),
    make_task=create_task.make_task,
)

WEBAPP_EDIT = SuiteSpec(
    name="webapp_edit",
    cases_path=Path(__file__).parent / "webapp_edit" / "cases.yaml",
    input_type=WebappEditInput,
    output_type=ProposedWebappVersion,
    metadata_type=WebappEditMetadata,
    agent=EditWebappAgent,
    evaluators=(webapp_edit_evaluators.ProposalChecks(),),
    make_task=webapp_edit_task.make_task,
    environment=webapp_edit_task.git_server,
)

SUITES: dict[str, SuiteSpec] = {
    suite.name: suite for suite in (PIPELINE_CREATE, WEBAPP_EDIT)
}


def get_suite(name: str) -> SuiteSpec:
    if name not in SUITES:
        raise KeyError(
            f"Unknown suite {name!r}. Known suites: {', '.join(sorted(SUITES))}."
        )
    return SUITES[name]
