"""Workspace duplication orchestrator.

Owns the ordered registry of resource copiers and runs the selected ones in
dependency order: workspace metadata first (it creates the target and yields its
handle), files before pipelines (notebook pipelines need their .ipynb present
first). The medium (ORM vs GraphQL) is decided per endpoint inside each copier,
so this orchestration is written once and shared by every flow (CLI + admin).
"""

from collections.abc import Iterable

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.progress import ProgressReporter
from hexa.workspace_duplicator.resources.base import ResourceCopier
from hexa.workspace_duplicator.resources.connections import ConnectionsCopier
from hexa.workspace_duplicator.resources.database import DatabaseCopier
from hexa.workspace_duplicator.resources.files import FilesCopier
from hexa.workspace_duplicator.resources.pipelines import PipelinesCopier
from hexa.workspace_duplicator.resources.workspace import WorkspaceMetadataCopier
from hexa.workspace_duplicator.results import DuplicationResult

WORKSPACE_COPIERS: list[ResourceCopier] = [
    WorkspaceMetadataCopier(),  # Mandatory first step
    FilesCopier(),  # Before pipelines, needed for .ipynb files (notebook pipelines)
    DatabaseCopier(),  # LOCAL→LOCAL: native pg; else skip + warning
    ConnectionsCopier(),
    PipelinesCopier(),
    # DatasetsCopier(),  # future — append here
]


def _resolve_selection(
    copiers: Iterable[ResourceCopier], resources: set[str] | None
) -> list[ResourceCopier]:
    """Filter the registry to the chosen names.

    Force-includes any ``mandatory`` copier and preserves registry order so
    dependency ordering can't be broken by selection. ``resources=None`` means
    "all".
    """
    if resources is None:
        return list(copiers)
    return [c for c in copiers if c.mandatory or c.name in resources]


def duplicate_workspace(
    source: Endpoint,
    target: Endpoint,
    reporter: ProgressReporter,
    *,
    resources: set[str] | None = None,
) -> DuplicationResult:
    """Duplicate a workspace from ``source`` to ``target``.

    Runs the selected copiers in registry (dependency) order, recording the
    outcome on a single :class:`DuplicationResult`. Live progress is emitted
    through ``reporter``; pass a :class:`~hexa.workspace_duplicator.progress.NullReporter`
    to discard it.
    """
    selected = _resolve_selection(WORKSPACE_COPIERS, resources)
    selected_names = {c.name for c in selected}
    result = DuplicationResult()
    for copier in selected:
        for dep in copier.depends_on:
            if dep not in selected_names:
                message = f"{copier.name}: dependency '{dep}' not selected — may be incomplete"
                result.warn(message)
                reporter.warning(message)
        reporter.info(f"=> Copying {copier.name} ...")
        copier.copy(source, target, result, reporter)
    return result
