"""The types of a webapp_edit case, and of the version the agent proposed."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ...fixtures import webapp_slugs


class WebappEditInput(BaseModel):
    prompt: str
    fixture_profile: str
    webapp: str

    @field_validator("webapp")
    @classmethod
    def _seeded(cls, value: str) -> str:
        if value not in webapp_slugs():
            raise ValueError(
                f"Unknown webapp {value!r}. Known webapps: {', '.join(webapp_slugs())}."
            )
        return value


class FileCheck(BaseModel):
    """Patterns the proposed version of one file must, or must not, match.

    Regular expressions, case-insensitive, searched anywhere in the file. A
    character class like `[^}]*` spans lines, which is how a check pins a key to
    one block of a file.
    """

    path: str
    contains: list[str] = Field(default_factory=list)
    not_contains: list[str] = Field(default_factory=list)

    @field_validator("contains", "not_contains")
    @classmethod
    def _compiles(cls, patterns: list[str]) -> list[str]:
        for pattern in patterns:
            re.compile(pattern)
        return patterns

    def failures(self, content: str | None) -> list[str]:
        if content is None:
            return [f"{self.path}: missing from the proposal"]
        failed = [
            f"{self.path}: no match for {pattern!r}"
            for pattern in self.contains
            if not re.search(pattern, content, re.IGNORECASE)
        ]
        failed += [
            f"{self.path}: still matches {pattern!r}"
            for pattern in self.not_contains
            if re.search(pattern, content, re.IGNORECASE)
        ]
        return failed


class WebappEditMetadata(BaseModel):
    task_id: str
    lang: Literal["en", "fr"]
    checks: list[FileCheck]
    # Files the request may reasonably touch besides the checked ones, such as a
    # README naming the page that was renamed.
    may_change: list[str] = Field(default_factory=list)
    surface_tags: list[str] = Field(default_factory=list)
    difficulty: str | None = None
    notes: str | None = None


class ProposedWebappVersion(BaseModel):
    """The last version the agent proposed successfully, as the full file set.

    `files` is None when no proposal went through, which is not the same as an
    empty web app.
    """

    files: dict[str, str] | None = None
    deleted_paths: list[str] = Field(default_factory=list)
    commit_message: str | None = None
    final_text: str | None = None
    tool_calls: list[str] = Field(default_factory=list)
    rejected_proposals: int = 0
