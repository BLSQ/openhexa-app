from collections.abc import Mapping

from .grep import GREP_HEAD_LIMIT, GrepOutputMode, grep
from .path_pattern import PathPattern
from .window import read_window

GLOB_LIMIT = 100


class TextFiles:
    """Text files by path: the common ground of every file source.

    It only needs a mapping, so a source can load contents lazily: `glob` touches
    paths alone, and `grep` reads only the files its `glob` filter keeps, stopping
    once it has a full page.
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
        """Search file contents (see grep.grep), restricted to paths matching `glob`."""
        return grep(
            ((path, self._files[path]) for path in self._paths(glob)),
            pattern,
            output_mode=output_mode,
            ignore_case=ignore_case,
            context=context,
            head_limit=head_limit,
            offset=offset,
        )

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
        """A window of a file's lines (see window.read_window)."""
        if path not in self._files:
            return {"error": f"File not found: {path}"}
        return read_window(
            self._files[path],
            start_line,
            end_line,
            line_numbers=line_numbers,
            max_lines=max_lines,
            max_line_chars=max_line_chars,
        )

    def _paths(self, pattern: str | None) -> list[str]:
        if pattern is None:
            return sorted(self._files)
        path_pattern = PathPattern(pattern)
        return sorted(p for p in self._files if path_pattern.matches(p))
