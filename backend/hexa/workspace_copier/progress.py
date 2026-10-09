"""Progress reporting for the copy flows.

The script (orchestrator + copiers) never writes to stdout or calls ``print``
directly. Instead it emits progress through a :class:`ProgressReporter` that each
entrypoint supplies:

* CLI -> :class:`StreamReporter` writing live to ``self.stdout``.
* Admin view -> :class:`BufferReporter`, rendered into the page after the run.
* Async job -> :class:`DatabaseReporter`, appending to the run record.
"""

import time
from datetime import datetime
from typing import Protocol, runtime_checkable

from django.db.models import F, TextField, Value
from django.db.models.functions import Concat
from django.utils import timezone

from hexa.workspace_copier.models import WorkspaceCopyRun

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

    Used by the (synchronous) template copy admin view.
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


class DatabaseReporter(BaseReporter):
    """Append progress to a :class:`WorkspaceCopyRun`'s logs (async job).

    A large copy logs one line per file, so lines are buffered and appended in
    batches rather than written one by one. Warnings and errors flush at once
    so problems show up on the run page without waiting for the next batch.
    """

    def __init__(
        self,
        run: WorkspaceCopyRun,
        *,
        flush_interval: float = 2.0,
        max_buffer: int = 50,
    ):
        self.run_id = run.pk
        self.flush_interval = flush_interval
        self.max_buffer = max_buffer
        self.buffer: list[str] = []
        self._last_flush = time.monotonic()

    def log(self, message: str, *, level: str = "INFO") -> None:
        self.buffer.append(format_entry(timezone.localtime(), level, message))
        if (
            level != "INFO"
            or len(self.buffer) >= self.max_buffer
            or time.monotonic() - self._last_flush >= self.flush_interval
        ):
            self.flush()

    def flush(self) -> None:
        if not self.buffer:
            return
        chunk = "".join(f"{line}\n" for line in self.buffer)
        self.buffer = []
        self._last_flush = time.monotonic()
        # Appending in SQL avoids re-reading and rewriting the whole log on
        # every flush, and can't overwrite a concurrent status update.
        WorkspaceCopyRun.objects.filter(pk=self.run_id).update(
            logs=Concat(F("logs"), Value(chunk), output_field=TextField()),
            updated_at=timezone.now(),
        )
