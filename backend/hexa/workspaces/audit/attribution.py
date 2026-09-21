"""Which workspace an object belongs to."""

from collections.abc import Iterator
from typing import NamedTuple
from uuid import UUID

from django.db.models import Model

from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile
from hexa.workspaces.models import Workspace


class IndirectOwner(NamedTuple):
    """How to get the workspace of an object with no workspace_id attribute.

    ``fk`` points to the linked object that has the workspace information.
    A page of objects collapses to the few parents/workspaces it hangs from;
    those parents are then resolved in one query at the end of the request
    using ``workspace_path`` and ``dataset_path`` to get the workspace.
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


def resolve_indirect_owners(
    pending: dict[type[Model], set],
) -> Iterator[tuple[UUID, str, UUID]]:
    """Yields ``(workspace_id, model_name, dataset_id)`` for every object parent it finds."""
    for model, owner in INDIRECT_OWNERS.items():
        parent_ids = pending[model]
        if not parent_ids:
            continue
        for workspace_id, dataset_id in owner.parent._base_manager.filter(
            pk__in=parent_ids
        ).values_list(owner.workspace_path, owner.dataset_path):
            if workspace_id is not None:
                yield workspace_id, model.__name__, dataset_id


class TrackingPlan(NamedTuple):
    """What to read off an instance of one model class, decided once per class.

    ``_observe`` runs on every object of every response, so everything that depends only
    on the class - its name, whether it reaches its workspace directly or through a
    parent, which attributes hold the ids - is resolved here once instead of there.
    """

    name: str
    tracked_as: type[Model] | None
    owner: IndirectOwner | None
    workspace_attr: str | None
    dataset_attr: str | None


_PLANS: dict[type, TrackingPlan | None] = {}


def tracking_plan(cls: type) -> TrackingPlan | None:
    """The plan for ``cls``, or ``None`` if instances of it say nothing about scope."""
    try:
        return _PLANS[cls]
    except KeyError:
        pass

    plan = None
    if issubclass(cls, Model):
        attnames = {field.attname for field in cls._meta.concrete_fields}
        for tracked_as, owner in INDIRECT_OWNERS.items():
            if issubclass(cls, tracked_as):
                plan = TrackingPlan(cls.__name__, tracked_as, owner, None, None)
                break
        else:
            if issubclass(cls, Workspace):
                workspace_attr = "id"
            else:
                workspace_attr = "workspace_id" if "workspace_id" in attnames else None
            if workspace_attr:
                # A dataset link reached from another workspace is classified by the
                # dataset it points at, not by the link itself.
                if issubclass(cls, Dataset):
                    dataset_attr = "id"
                else:
                    dataset_attr = "dataset_id" if "dataset_id" in attnames else None
                plan = TrackingPlan(
                    cls.__name__, None, None, workspace_attr, dataset_attr
                )

    _PLANS[cls] = plan
    return plan
