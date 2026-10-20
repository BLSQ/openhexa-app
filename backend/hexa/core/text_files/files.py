from collections.abc import Iterable, Mapping

from .grep import GREP_HEAD_LIMIT, GrepOutputMode, grep
from .overlay import Overlay
from .path_pattern import PathPattern
from .window import ReadOptions, read_window

GLOB_LIMIT = 100


class TextFiles:
    """Glob, grep and read over files by path: a FileSource, or any mapping that
    follows its contract (a dict in tests, an Overlay of pending changes).

    Sources load contents lazily, so `glob` touches paths alone, and `grep` reads only
    the files its `glob` filter keeps, stopping once it has a full page. A file whose
    content is None (binary, too large) is still listed by `glob` but skipped by `grep`
    and refused by `read`.
    """

    def __init__(self, files: Mapping[str, str | None]):
        self._files = files

    def with_changes(
        self, changes: Mapping[str, str], deleted: Iterable[str] = ()
    ) -> "TextFiles":
        """These files as seen through uncommitted changes, e.g. a pending proposal."""
        return TextFiles(Overlay(self._files, changes, deleted))

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
            (
                (path, text)
                for path in self._paths(glob)
                if (text := self._files[path]) is not None
            ),
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
        options: ReadOptions = ReadOptions(),
    ) -> dict:
        """A window of a file's lines (see window.read_window)."""
        if path not in self._files:
            return {"error": f"File not found: {path}"}
        text = self._files[path]
        if text is None:
            return {"error": f"Not a readable text file: {path}"}
        return read_window(text, start_line, end_line, options)

    def _paths(self, pattern: str | None) -> list[str]:
        if pattern is None:
            return sorted(self._files)
        path_pattern = PathPattern(pattern)
        return sorted(p for p in self._files if path_pattern.matches(p))
