"""Glob, grep and windowed reads over a set of text files.

The API mirrors Claude Code's Glob, Grep and Read tools, which models already know
how to drive.
"""

import re
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from glob import translate as translate_glob

GLOB_LIMIT = 100
GREP_HEAD_LIMIT = 250
# Minified JS/CSS can put a whole file on one line; a single match must not flood the context.
GREP_MAX_LINE_CHARS = 300


class GrepOutputMode(StrEnum):
    FILES_WITH_MATCHES = "files_with_matches"
    CONTENT = "content"
    COUNT = "count"


class TextFiles:
    """Text files by path: the common ground of every file source.

    It only needs a mapping, so a source can load contents lazily: `glob` touches
    paths alone, and `grep` reads only the files its `glob` filter keeps.
    """

    def __init__(self, files: Mapping[str, str]):
        self._files = files

    def glob(self, pattern: str, limit: int = GLOB_LIMIT) -> dict:
        """Paths matching a glob pattern (see PathPattern), sorted."""
        paths = self._paths(pattern)
        return {"paths": paths[:limit], "truncated": len(paths) > limit}

    def grep(
        self,
        pattern: str,
        *,
        glob: str | None = None,
        output_mode: GrepOutputMode = GrepOutputMode.FILES_WITH_MATCHES,
        ignore_case: bool = False,
        context: int = 0,
        head_limit: int = GREP_HEAD_LIMIT,
        offset: int = 0,
    ) -> dict:
        """Search file contents line by line with a Python regular expression.

        `head_limit` and `offset` page through the entries of the chosen mode: file
        paths, output lines, or per-file counts. Files are read lazily and the search
        stops once the page is filled, except in `count` mode, whose total covers every
        match.
        """
        try:
            # MULTILINE keeps `^` and `$` anchored to lines in the whole-text prefilter.
            regex = re.compile(
                pattern, re.MULTILINE | (re.IGNORECASE if ignore_case else 0)
            )
        except re.error as e:
            return {"error": f"Invalid regular expression {pattern!r}: {e}"}

        mode = _GREP_MODES[output_mode]
        limit = offset + head_limit
        entries: list = []
        for hit in self._hits(regex, glob):
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

    def read(
        self,
        path: str,
        start_line: int | None = None,
        end_line: int | None = None,
        *,
        line_numbers: bool = False,
        max_lines: int | None = None,
        max_line_chars: int | None = None,
    ) -> dict:
        """A 1-indexed, inclusive window of a file's lines, with its total line count.

        `max_lines` caps the window and adds a notice telling how to read the rest;
        `line_numbers` prefixes each line `cat -n` style; `max_line_chars` clips long lines.
        """
        if path not in self._files:
            return {"error": f"File not found: {path}"}

        lines = _split_lines(self._files[path])
        total = len(lines)
        start = max(start_line or 1, 1)
        end = min(end_line or total, total)
        result = {"start_line": start, "end_line": end, "total_lines": total}

        if total == 0:
            return {**result, "content": "", "notice": "The file is empty."}
        if start > total:
            return {
                **result,
                "content": "",
                "notice": f"start_line {start} is past the end of the file ({total} lines).",
            }
        if max_lines is not None and end - start + 1 > max_lines:
            end = result["end_line"] = start + max_lines - 1
            result["notice"] = (
                f"PARTIAL view: lines {start}-{end} of {total}. Pass start_line and "
                "end_line to read another section, or grep for the content you need."
            )

        window = (_clip(line, max_line_chars) for line in lines[start - 1 : end])
        if line_numbers:
            window = (f"{n:>6}\t{line}" for n, line in enumerate(window, start))
        return {**result, "content": "\n".join(window)}

    def _paths(self, pattern: str | None) -> list[str]:
        if pattern is None:
            return sorted(self._files)
        path_pattern = PathPattern(pattern)
        return sorted(p for p in self._files if path_pattern.matches(p))

    def _hits(self, regex: re.Pattern, glob: str | None) -> Iterator["_FileHits"]:
        # A whole-text search runs in C and rules out most files without splitting them
        # into lines. `\A` and `\Z` anchor to each line in the per-line pass but to the
        # whole text here, so such patterns skip this shortcut.
        prefilter = not re.search(r"\\[AZ]", regex.pattern)
        for path in self._paths(glob):
            text = self._files[path]
            if prefilter and not regex.search(text):
                continue
            if hit := _FileHits.search(path, text, regex):
                yield hit


@dataclass(frozen=True)
class PathPattern:
    """A glob pattern: `*` stays within a directory, `**` spans any depth (including
    none) and `{a,b}` lists alternatives, e.g. `**/*.js`, `src/**/*.ts`, `*.{json,yaml}`.
    """

    pattern: str

    def matches(self, path: str) -> bool:
        return self._regex.match(path) is not None

    @cached_property
    def _regex(self) -> re.Pattern:
        return re.compile(
            "|".join(
                translate_glob(alternative, recursive=True, include_hidden=True)
                for alternative in self._expand_braces(self.pattern)
            )
        )

    @classmethod
    def _expand_braces(cls, pattern: str) -> list[str]:
        # glob.translate has no brace support, but `*.{js,css}` is the idiom models reach for.
        match = re.search(r"\{([^{}]*)\}", pattern)
        if match is None:
            return [pattern]
        head, tail = pattern[: match.start()], pattern[match.end() :]
        return [
            expanded
            for option in match.group(1).split(",")
            for expanded in cls._expand_braces(head + option + tail)
        ]


@dataclass(frozen=True)
class _FileHits:
    path: str
    lines: list[str]
    indexes: list[int]

    @classmethod
    def search(cls, path: str, text: str, regex: re.Pattern) -> "_FileHits | None":
        lines = _split_lines(text)
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
                line = _clip(self.lines[i], GREP_MAX_LINE_CHARS)
                output.append(f"{self.path}{sep}{i + 1}{sep}{line}")
            last = max(last, end)
        return output


class _GrepMode(ABC):
    """How one output mode turns file hits into entries, and a page of them into a result."""

    # Whether the search can stop once the page is filled, sparing reads of later files.
    stops_early = True

    @abstractmethod
    def entries(self, hit: _FileHits, context: int) -> list:
        ...

    @abstractmethod
    def render(self, page: list, entries: list) -> dict:
        ...


class _FilesWithMatches(_GrepMode):
    def entries(self, hit, context):
        return [hit.path]

    def render(self, page, entries):
        return {"files": page}


class _Content(_GrepMode):
    def entries(self, hit, context):
        return hit.content_lines(context)

    def render(self, page, entries):
        return {"content": "\n".join(page)}


class _Count(_GrepMode):
    # The total covers every match, so every file must be searched.
    stops_early = False

    def entries(self, hit, context):
        return [(hit.path, len(hit.indexes))]

    def render(self, page, entries):
        return {"counts": dict(page), "total": sum(count for _, count in entries)}


_GREP_MODES: dict[GrepOutputMode, _GrepMode] = {
    GrepOutputMode.FILES_WITH_MATCHES: _FilesWithMatches(),
    GrepOutputMode.CONTENT: _Content(),
    GrepOutputMode.COUNT: _Count(),
}


def _split_lines(text: str) -> list[str]:
    # Unlike str.splitlines, only "\n" ends a line, so numbers match what editors show.
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def _clip(line: str, max_chars: int | None) -> str:
    if max_chars is None or len(line) <= max_chars:
        return line
    return f"{line[:max_chars]}… [{len(line) - max_chars} more characters]"
