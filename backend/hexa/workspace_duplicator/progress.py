"""Progress reporting for the duplication flows.

The script (orchestrator + copiers) never writes to stdout or calls ``print``
directly. Instead it emits progress through a :class:`ProgressReporter` that each
entrypoint supplies:

* CLI -> :class:`StreamReporter` writing live to ``self.stdout``.
* Admin view -> :class:`BufferReporter`, rendered into the page after the run.
* Async job (future ``CopyWorkspaceRun``) -> a reporter that appends to the run
  record; see :class:`BufferReporter` for the shape such a class would follow.

This keeps the script independent of its caller and, because each run gets its
own reporter instance, avoids the global-state pitfalls of module-level logging
when several runs share a process. It is deliberately separate from the
``--debug`` wire-level logging in :mod:`transport`, which stays developer-only.
"""

from typing import Protocol, runtime_checkable

# Ordered low -> high so a reporter can filter by a minimum level.
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


@runtime_checkable
class ProgressReporter(Protocol):
    def log(self, message: str, *, level: str = "INFO") -> None: ...


class BaseReporter:
    """Convenience helpers; concrete reporters only implement :meth:`log`."""

    def log(self, message: str, *, level: str = "INFO") -> None:
        raise NotImplementedError

    def info(self, message: str) -> None:
        self.log(message, level="INFO")

    def warning(self, message: str) -> None:
        self.log(message, level="WARNING")

    def debug(self, message: str) -> None:
        self.log(message, level="DEBUG")

    def error(self, message: str) -> None:
        self.log(message, level="ERROR")


class NullReporter(BaseReporter):
    """Discards everything. Default so the script can run without a caller."""

    def log(self, message: str, *, level: str = "INFO") -> None:
        pass


class StreamReporter(BaseReporter):
    """Write progress live to a stream (CLI: ``self.stdout``).

    ``verbose`` mirrors ``--debug``: DEBUG-level lines are dropped unless set.
    """

    def __init__(self, stream, *, verbose: bool = False):
        self.stream = stream
        self.verbose = verbose

    def log(self, message: str, *, level: str = "INFO") -> None:
        if level == "DEBUG" and not self.verbose:
            return
        prefix = "" if level == "INFO" else f"[{level}] "
        self.stream.write(f"{prefix}{message}\n")


class BufferReporter(BaseReporter):
    """Collect lines in memory for rendering after the run (admin view).

    The future ``CopyWorkspaceRun`` reporter would follow the same shape but,
    instead of appending to a list, buffer and periodically flush to the record
    (saving every N lines and once more in a ``finally``).
    """

    def __init__(self):
        self.entries: list[tuple[str, str]] = []

    def log(self, message: str, *, level: str = "INFO") -> None:
        self.entries.append((level, message))

    def render(self) -> str:
        return "\n".join(
            msg if level == "INFO" else f"[{level}] {msg}"
            for level, msg in self.entries
        )
