"""Progress reporting for the copy flows.

The script (orchestrator + copiers) never writes to stdout or calls ``print``
directly. Instead it emits progress through a :class:`ProgressReporter` that each
entrypoint supplies:

* CLI -> :class:`StreamReporter` writing live to ``self.stdout``.
* Admin view -> :class:`BufferReporter`, rendered into the page after the run.
* Async job (future feature) -> a reporter that appends to the run
  record; see :class:`BufferReporter` for the shape such a class would follow.
"""

from typing import Protocol, runtime_checkable

# Ordered low -> high so a reporter can filter by a minimum level.
LEVELS = ("INFO", "WARNING", "ERROR")


@runtime_checkable
class ProgressReporter(Protocol):
    def log(self, message: str, *, level: str = "INFO") -> None:
        ...


class BaseReporter:
    def log(self, message: str, *, level: str = "INFO") -> None:
        raise NotImplementedError

    def info(self, message: str) -> None:
        self.log(message, level="INFO")

    def warning(self, message: str) -> None:
        self.log(message, level="WARNING")

    def error(self, message: str) -> None:
        self.log(message, level="ERROR")


class NullReporter(BaseReporter):
    """Discards everything. Default so the script can run without a caller.

    Used in backend tests.
    """

    def log(self, message: str, *, level: str = "INFO") -> None:
        pass


class StreamReporter(BaseReporter):
    """Write progress live to a stream (CLI: ``self.stdout``)."""

    def __init__(self, stream):
        self.stream = stream

    def log(self, message: str, *, level: str = "INFO") -> None:
        prefix = "" if level == "INFO" else f"[{level}] "
        self.stream.write(f"{prefix}{message}\n")


class BufferReporter(BaseReporter):
    """Collect lines in memory for rendering after the run.

    This is used in the Django admin view. Later, we'll adapt this reporter
    to add lines to the "logs" field on a "run" records, when we run the copier
    in a async job.
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
