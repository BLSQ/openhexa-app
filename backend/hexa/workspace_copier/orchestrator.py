"""Workspace copy orchestrator.

Owns the ordered registry of resource copiers and runs the selected ones in
dependency order: workspace metadata first (it creates the target and yields its
handle), then the rest. The medium (ORM vs GraphQL) is decided per endpoint
inside each copier, so this orchestration is written once and shared by every
flow (CLI + admin).
"""

from collections.abc import Iterable

from django.utils import timezone

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import ProgressReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.resources.connections import ConnectionsCopier
from hexa.workspace_copier.resources.database import DatabaseCopier
from hexa.workspace_copier.resources.datasets import DatasetsCopier
from hexa.workspace_copier.resources.files import FilesCopier
from hexa.workspace_copier.resources.pipelines import PipelinesCopier
from hexa.workspace_copier.resources.workspace import WorkspaceMetadataCopier
from hexa.workspace_copier.results import CopyResult

WORKSPACE_COPIERS: list[ResourceCopier] = [
    WorkspaceMetadataCopier(),  # Mandatory first step
    FilesCopier(),
    DatabaseCopier(),  # LOCAL→LOCAL: native pg; else skip + warning
    ConnectionsCopier(),
    PipelinesCopier(),
    DatasetsCopier(),
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


def copy_workspace(
    source: Endpoint,
    target: Endpoint,
    reporter: ProgressReporter,
    *,
    resources: set[str] | None = None,
    options: CopyOptions = CopyOptions(),
) -> CopyResult:
    """Copy a workspace from ``source`` to ``target``.

    Runs the selected copiers in registry (dependency) order, recording the
    outcome on a single :class:`CopyResult`. Live progress is emitted
    through ``reporter``; pass a :class:`~hexa.workspace_copier.progress.NullReporter`
    to discard it. ``options`` carries the run-wide switches (see
    :class:`~hexa.workspace_copier.options.CopyOptions`); every copier receives
    them and reads only what concerns it.
    """
    selected = _resolve_selection(WORKSPACE_COPIERS, resources)
    selected_names = {c.name for c in selected}
    result = CopyResult(started_at=timezone.localtime())
    for copier in selected:
        for dep in copier.depends_on:
            if dep not in selected_names:
                message = f"{copier.name}: dependency '{dep}' not selected — may be incomplete"
                result.warn(message)
                reporter.warning(message)
        reporter.info(f"=> Copying {copier.name} ...")
        copier.copy(source, target, result, reporter, options=options)
        # Every line is timestamped, so bracketing each copier with a start and
        # a finish line is what makes "how long did files take" answerable —
        # including for the last copier, which has no successor line.
        reporter.info(f"   {copier.name} finished")
    result.finished_at = timezone.localtime()
    return result
