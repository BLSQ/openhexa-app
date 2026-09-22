"""Pulling cases from the hosted Logfire dataset, and proving they are runnable.

Cases live server-side and are editable in the Logfire UI, which has no PR
review. The harness therefore detects drift rather than preventing it. Every
experiment is stamped with a hash of the cases it ran, so an edited dataset
shows up as a changed hash instead of silently explaining a moved score.
"""

from __future__ import annotations

import hashlib
import json
import os
import re

from logfire.experimental.api_client import LogfireAPIClient
from pydantic_evals import Dataset

from hexa.assistant.instructions import get_instructions

from ..fixtures import profile_spec
from ..suites import SuiteSpec

TOKEN_ENV_VARS = ("LOGFIRE_DATASET_TOKEN", "LOGFIRE_TOKEN")

# logfire only reads the region out of a token whose body is alphanumeric, and
# dataset tokens have a UUID-style body. The match fails, logfire falls back to
# the US endpoint, and an EU token is rejected there with a 401. Parse the region
# ourselves. LOGFIRE_BASE_URL overrides for self-hosted.
_TOKEN_REGION = re.compile(r"^pylf_v\d+_(?P<region>[a-z]{2})_")


class DatasetError(RuntimeError):
    pass


def _token() -> str:
    for name in TOKEN_ENV_VARS:
        value = (os.environ.get(name) or "").strip().strip("\"'")
        if value:
            return value
    raise DatasetError(
        f"No Logfire API key found. Set one of: {', '.join(TOKEN_ENV_VARS)}."
    )


def _base_url(token: str) -> str | None:
    override = (os.environ.get("LOGFIRE_BASE_URL") or "").strip()
    if override:
        return override
    match = _TOKEN_REGION.match(token)
    return f"https://logfire-{match['region']}.pydantic.dev" if match else None


def pull_dataset(suite: SuiteSpec) -> Dataset:
    token = _token()
    with LogfireAPIClient(api_key=token, base_url=_base_url(token)) as client:
        dataset = client.get_dataset(
            suite.dataset_name,
            input_type=suite.input_type,
            output_type=suite.output_type,
            metadata_type=suite.metadata_type,
        )
    if not isinstance(dataset, Dataset):
        raise DatasetError(
            f"{suite.dataset_name!r} did not come back as an evaluable dataset."
        )
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
        "dataset_name": suite.dataset_name,
        "dataset_hash": dataset_hash(dataset),
        "case_count": len(dataset.cases),
        "model": model,
        "instructions_hash": instructions_hash(suite.instruction_set),
    }
