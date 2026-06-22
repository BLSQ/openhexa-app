"""Workspace database copier.

Runs a native Postgres copy only when **both** endpoints are LOCAL (same
cluster). If either side is REMOTE it records a warning and returns, matching
today's out-of-scope behaviour (the standalone script never copied the DB). The
native local copy is implemented in a later phase.
"""

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.progress import ProgressReporter
from hexa.workspace_duplicator.resources.base import ResourceCopier
from hexa.workspace_duplicator.results import DuplicationResult


class DatabaseCopier(ResourceCopier):
    name = "database"
    label = "Workspace database"

    def copy(
        self,
        source: Endpoint,
        target: Endpoint,
        result: DuplicationResult,
        reporter: ProgressReporter,
    ) -> None:
        if source.is_remote or target.is_remote:
            message = (
                "Database not copied — both endpoints must be local (same cluster)."
            )
            result.warn(message)
            reporter.warning(f"   {message}")
            return
        self._copy_local(source, target, result)

    def _copy_local(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None:
        raise NotImplementedError(
            "Native local database copy is implemented in a later phase"
        )
