import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import StrEnum

from .lines import clip, split_lines

GREP_HEAD_LIMIT = 250
# Minified JS/CSS can put a whole file on one line; a single match must not flood the context.
GREP_MAX_LINE_CHARS = 300


class GrepOutputMode(StrEnum):
    FILES_WITH_MATCHES = "files_with_matches"
    CONTENT = "content"
    COUNT = "count"


def grep(
    candidates: Iterable[tuple[str, str]],
    pattern: str,
    *,
    output_mode: GrepOutputMode = GrepOutputMode.FILES_WITH_MATCHES,
    ignore_case: bool = False,
    context: int = 0,
    head_limit: int = GREP_HEAD_LIMIT,
    offset: int = 0,
) -> dict:
    """Search `(path, text)` candidates line by line with a Python regular expression.

    `head_limit` and `offset` page through the entries of the chosen mode: file
    paths, output lines, or per-file counts.

    Built to touch as little as possible:
    - candidates are consumed lazily and the search stops one entry past the page,
      so a lazy source loads no further files; `count` mode reads everything, since
      its total covers every match;
    - each file is first searched as a whole, which rules out non-matching files
      without splitting them into lines (about 10x faster on files with no match).
    """
    try:
        # MULTILINE keeps `^` and `$` anchored to lines in the whole-text prefilter.
        regex = re.compile(
            pattern, re.MULTILINE | (re.IGNORECASE if ignore_case else 0)
        )
    except re.error as e:
        return {"error": f"Invalid regular expression {pattern!r}: {e}"}

    mode = _MODES[output_mode]
    limit = offset + head_limit
    entries: list = []
    for hit in _hits(candidates, regex):
        entries.extend(mode.entries(hit, context))
        # One entry past the page is enough to know the result is truncated.
        if mode.stops_early and len(entries) > limit:
            break

    page = entries[offset:limit]
    result = {**mode.render(page, entries), "truncated": len(entries) > limit}
    if entries and not page:
        # An empty page means the loop never stopped early, so the count is exact.
        result[
            "notice"
        ] = f"No entries at offset {offset}: there are {len(entries)} in total."
    return result


def _hits(
    candidates: Iterable[tuple[str, str]], regex: re.Pattern
) -> Iterator["_FileHits"]:
    # A whole-text search runs in C and rules out most files without splitting them
    # into lines. `\A` and `\Z` anchor to each line in the per-line pass but to the
    # whole text here, so such patterns skip this shortcut.
    prefilter = not re.search(r"\\[AZ]", regex.pattern)
    for path, text in candidates:
        if prefilter and not regex.search(text):
            continue
        if hit := _FileHits.search(path, text, regex):
            yield hit


@dataclass(frozen=True)
class _FileHits:
    path: str
    lines: list[str]
    indexes: list[int]

    @classmethod
    def search(cls, path: str, text: str, regex: re.Pattern) -> "_FileHits | None":
        lines = split_lines(text)
        indexes = [i for i, line in enumerate(lines) if regex.search(line)]
        return cls(path, lines, indexes) if indexes else None

    def content_lines(self, context: int) -> list[str]:
        """ripgrep-style: `path:N:line` for matches, `path-N-line` for context, `--` between gaps."""
        hit_set = set(self.indexes)
        output: list[str] = []
        last = -1
        for hit in self.indexes:
            start = max(hit - context, last + 1)
            end = min(hit + context, len(self.lines) - 1)
            if output and start > last + 1:
                output.append("--")
            for i in range(start, end + 1):
                sep = ":" if i in hit_set else "-"
                line = clip(self.lines[i], GREP_MAX_LINE_CHARS)
                output.append(f"{self.path}{sep}{i + 1}{sep}{line}")
            last = max(last, end)
        return output


class _Mode(ABC):
    """How one output mode turns file hits into entries, and a page of them into a result."""

    # Whether the search can stop once the page is filled, sparing reads of later files.
    stops_early = True

    @abstractmethod
    def entries(self, hit: _FileHits, context: int) -> list:
        ...

    @abstractmethod
    def render(self, page: list, entries: list) -> dict:
        ...


class _FilesWithMatches(_Mode):
    def entries(self, hit, context):
        return [hit.path]

    def render(self, page, entries):
        return {"files": page}


class _Content(_Mode):
    def entries(self, hit, context):
        return hit.content_lines(context)

    def render(self, page, entries):
        return {"content": "\n".join(page)}


class _Count(_Mode):
    # The total covers every match, so every file must be searched.
    stops_early = False

    def entries(self, hit, context):
        return [(hit.path, len(hit.indexes))]

    def render(self, page, entries):
        return {"counts": dict(page), "total": sum(count for _, count in entries)}


_MODES: dict[GrepOutputMode, _Mode] = {
    GrepOutputMode.FILES_WITH_MATCHES: _FilesWithMatches(),
    GrepOutputMode.CONTENT: _Content(),
    GrepOutputMode.COUNT: _Count(),
}
