"""ResourceCopier: the one abstraction the orchestrator relies on.

Each copier owns everything about one resource across both mediums. Within
``copy`` the read path branches on ``source.mode`` and the write path on
``target.mode`` (ORM when LOCAL, GraphQL when REMOTE), recording what it
did/skipped/failed on the shared :class:`DuplicationResult`.
"""

from abc import ABC, abstractmethod

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.results import DuplicationResult


class ResourceCopier(ABC):
    name: str
    """Stable id used in selection + summary (e.g. "connections")."""

    label: str
    """Human label for the admin checkbox."""

    mandatory: bool = False
    """Workspace metadata sets this True (it creates the target every run)."""

    depends_on: tuple[str, ...] = ()
    """Advisory: a warning is emitted if a declared dependency is deselected."""

    @abstractmethod
    def copy(
        self, source: Endpoint, target: Endpoint, result: DuplicationResult
    ) -> None: ...
