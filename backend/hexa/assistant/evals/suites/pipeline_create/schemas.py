"""The types of a pipeline_create case, and of what the agent produced.

`cases.yaml` is validated against these on load, and by `make t`. A case with a
missing or wrong field fails before any model call, rather than being scored as
a case the harness had misread.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PipelineCreateInput(BaseModel):
    prompt: str
    fixture_profile: str


class PipelineCreateMetadata(BaseModel):
    task_id: str
    lang: Literal["en", "fr"]
    source_template: str | None = None
    surface_tags: list[str] = Field(default_factory=list)
    difficulty: str | None = None
    notes: str | None = None


class ProposedPipeline(BaseModel):
    """What the agent produced. Gold answers would use the same type.

    Every field but `files` is optional, so a case can carry a reference solution
    for an LLM judge without the deterministic verifiers needing one.
    """

    name: str | None = None
    description: str | None = None
    functional_type: str | None = None
    files: dict[str, str] = Field(default_factory=dict)
    final_text: str | None = None
    tool_calls: list[str] = Field(default_factory=list)
