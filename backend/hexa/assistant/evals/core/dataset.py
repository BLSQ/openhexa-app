"""Loading a suite's cases, and proving they are runnable.

Cases live in a YAML file beside each suite and change through PR review like
any other code. Every experiment is still stamped with a hash of the cases it
ran: the container has no git checkout, so the hash is the only record on the
experiment of which cases produced its scores.
"""

from __future__ import annotations

import hashlib
import json

import yaml
from pydantic_evals import Dataset

from hexa.assistant.instructions import get_instructions

from ..fixtures import profile_spec
from ..suites import SuiteSpec


class DatasetError(RuntimeError):
    pass


def load_dataset(suite: SuiteSpec) -> Dataset:
    """Read and type-check the suite's cases file.

    A missing field, a wrong value or a duplicate case name fails here, before
    any model call, rather than as a misread case halfway through a run.
    """
    dataset_type = Dataset[suite.input_type, suite.output_type, suite.metadata_type]
    try:
        dataset = dataset_type.from_file(suite.cases_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise DatasetError(str(exc)) from exc
    dataset.evaluators = list(suite.evaluators)
    return dataset


def dataset_hash(dataset: Dataset) -> str:
    """Fingerprint of the cases actually run.

    Covers the case name, inputs and metadata: everything that changes what the
    agent is asked and how the result is sliced.
    """
    payload = [
        {
            "name": case.name,
            "inputs": case.inputs.model_dump(mode="json"),
            "metadata": case.metadata.model_dump(mode="json")
            if case.metadata
            else None,
        }
        for case in dataset.cases
    ]
    payload.sort(key=lambda entry: entry["name"] or "")
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return digest[:16]


def validate_cases(dataset: Dataset) -> None:
    """Fail before spending a single model call, not on case 40 of 48."""
    if not dataset.cases:
        raise DatasetError("Dataset contains no cases.")
    problems = []
    for case in dataset.cases:
        if case.metadata is None:
            problems.append(f"{case.name}: missing metadata")
        try:
            profile_spec(case.inputs.fixture_profile)
        except KeyError as exc:
            problems.append(f"{case.name}: {exc}")
    if problems:
        raise DatasetError("Cases are not runnable:\n  " + "\n  ".join(problems))


def instructions_hash(instruction_set) -> str:
    """Fingerprint of the prompt the agent ran with.

    Hashes the assembled instruction text rather than a git revision. The
    container has no checkout, and the assembled text is what decides behaviour:
    it inlines `docs/en/writing-pipelines.md` and `sdk.md`, so editing the docs
    moves this hash even when instructions.py is untouched.
    """
    text = get_instructions(instruction_set)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def experiment_metadata(dataset: Dataset, *, suite: SuiteSpec, model: str) -> dict:
    return {
        "suite": suite.name,
        "dataset_name": dataset.name,
        "dataset_hash": dataset_hash(dataset),
        "case_count": len(dataset.cases),
        "model": model,
        "instructions_hash": instructions_hash(suite.instruction_set),
    }
