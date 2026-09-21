"""Which workspace an observed object belongs to."""

from collections.abc import Iterator
from typing import NamedTuple
from uuid import UUID

from django.db.models import Model

from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile
from hexa.workspaces.models import Workspace


class IndirectOwner(NamedTuple):
    """How to reach the workspace of a model that has no workspace_id of its own.

    ``fk`` is read off the observed object, so a page of files collapses to the few
    parents it hangs from; those parents are then resolved in one query at the end of
    the request through ``workspace_path`` and ``dataset_path``.
    """

    fk: str
    parent: type[Model]
    workspace_path: str
    dataset_path: str


INDIRECT_OWNERS = {
    DatasetVersion: IndirectOwner(
        fk="dataset_id",
        parent=Dataset,
        workspace_path="workspace_id",
        dataset_path="id",
    ),
    DatasetVersionFile: IndirectOwner(
        fk="dataset_version_id",
        parent=DatasetVersion,
        workspace_path="dataset__workspace_id",
        dataset_path="dataset_id",
    ),
}


def workspace_id_of(obj: Model) -> UUID | None:
    """The workspace an object belongs to"""
    if isinstance(obj, Workspace):
        return obj.id
    return getattr(obj, "workspace_id", None)


def resolve_indirect_owners(
    pending: dict[type[Model], set],
) -> Iterator[tuple[UUID, str, UUID]]:
    """Attribute the parents collected during the request, one query per model.

    Yields ``(workspace_id, model_name, dataset_id)`` for every parent that resolves.
    """
    for model, owner in INDIRECT_OWNERS.items():
        parent_ids = pending[model]
        if not parent_ids:
            continue
        for workspace_id, dataset_id in owner.parent._base_manager.filter(
            pk__in=parent_ids
        ).values_list(owner.workspace_path, owner.dataset_path):
            if workspace_id is not None:
                yield workspace_id, model.__name__, dataset_id
