"""Progress reporting for the copy flows.

The script (orchestrator + copiers) never writes to stdout or calls ``print``
directly. Instead it emits progress through a :class:`ProgressReporter` that each
entrypoint supplies:

* CLI -> :class:`StreamReporter` writing live to ``self.stdout``.
* Admin view -> :class:`BufferReporter`, rendered into the page after the run.
* Async job (future feature) -> a reporter that appends to the run
  record; see :class:`BufferReporter` for the shape such a class would follow.
"""

from datetime import datetime
from typing import Protocol, runtime_checkable

from django.utils import timezone

# Ordered low -> high so a reporter can filter by a minimum level.
LEVELS = ("INFO", "WARNING", "ERROR")


def format_entry(timestamp: datetime, level: str, message: str) -> str:
    """Render one log line, shared by every reporter so they can't drift apart."""
    prefix = "" if level == "INFO" else f"[{level}] "
    return f"{timestamp.strftime('%H:%M:%S')} {prefix}{message}"


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
        self.stream.write(f"{format_entry(timezone.localtime(), level, message)}\n")
        self.stream.flush()


class BufferReporter(BaseReporter):
    """Collect lines in memory for rendering after the run.

    This is used in the Django admin view. Later, we'll adapt this reporter
    to add lines to the "logs" field on a "run" records, when we run the copier
    in a async job.
    """

    def __init__(self):
        self.entries: list[tuple[datetime, str, str]] = []

    def log(self, message: str, *, level: str = "INFO") -> None:
        self.entries.append((timezone.localtime(), level, message))

    def render(self) -> str:
        return "\n".join(
            format_entry(timestamp, level, message)
            for timestamp, level, message in self.entries
        )
