"""Glob, grep and windowed reads over a set of text files.

The API mirrors Claude Code's Glob, Grep and Read tools, which models already know
how to drive.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from pathlib import PurePosixPath

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
        paths, output lines, or per-file counts. The `count` total covers every match.
        """
        try:
            regex = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
        except re.error as e:
            return {"error": f"Invalid regular expression {pattern!r}: {e}"}

        hits = [
            hit
            for path in self._paths(glob)
            if (hit := _FileHits.search(path, self._files[path], regex))
        ]
        entries = [entry for hit in hits for entry in hit.entries(output_mode, context)]
        page = entries[offset : offset + head_limit]

        result = {
            **_render(output_mode, page),
            "truncated": offset + head_limit < len(entries),
        }
        if output_mode == GrepOutputMode.COUNT:
            result["total"] = sum(len(hit.indexes) for hit in hits)
        if entries and not page:
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


@dataclass(frozen=True)
class PathPattern:
    """A glob pattern: `*` stays within a directory, `**` spans any depth (including
    none) and `{a,b}` lists alternatives, e.g. `**/*.js`, `src/**/*.ts`, `*.{json,yaml}`.
    """

    pattern: str

    def matches(self, path: str) -> bool:
        return any(PurePosixPath(path).full_match(p) for p in self._alternatives)

    @cached_property
    def _alternatives(self) -> list[str]:
        return self._expand_braces(self.pattern)

    @classmethod
    def _expand_braces(cls, pattern: str) -> list[str]:
        # pathlib's matcher has no brace support, but `*.{js,css}` is the idiom models reach for.
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

    def entries(self, output_mode: GrepOutputMode, context: int) -> list:
        match output_mode:
            case GrepOutputMode.CONTENT:
                return self._content_lines(context)
            case GrepOutputMode.COUNT:
                return [(self.path, len(self.indexes))]
            case _:
                return [self.path]

    def _content_lines(self, context: int) -> list[str]:
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


def _render(output_mode: GrepOutputMode, page: list) -> dict:
    match output_mode:
        case GrepOutputMode.CONTENT:
            return {"content": "\n".join(page)}
        case GrepOutputMode.COUNT:
            return {"counts": dict(page)}
        case _:
            return {"files": page}


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
