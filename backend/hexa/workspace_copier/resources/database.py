"""Workspace database copier.

Runs a native Postgres copy only when **both** endpoints are LOCAL (same
cluster). If either side is REMOTE it records a warning and returns, matching
today's out-of-scope behaviour (the standalone script never copied the DB). The
native local copy is implemented in a later phase.
"""

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult


class DatabaseCopier(ResourceCopier):
    name = "database"
    label = "Workspace database"

    def copy(
        self,
        source: Endpoint,
        target: Endpoint,
        result: CopyResult,
        reporter: ProgressReporter,
    ) -> None:
        if source.is_remote or target.is_remote:
            message = (
                "Database not copied: both endpoints must be local on the (same instance). "
                "Please perform a manual pg_dump / pg_restore."
            )
            result.warn(message)
            reporter.warning(f"   {message}")
            return
        self._copy_local(source, target, result)

    def _copy_local(
        self, source: Endpoint, target: Endpoint, result: CopyResult
    ) -> None:
        raise NotImplementedError(
            "Native local database copy is implemented in a later phase"
        )
