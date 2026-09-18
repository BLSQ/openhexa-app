"""Phase 0 analysis for workspace-scoped tokens (HEXA-1775).

A workspace token today authenticates the *user*, not the workspace, so a
token issued for workspace A can reach everything its owner can reach. Before
changing that we need to know how much traffic would actually break, which is
what this measures: it observes token-authenticated GraphQL requests and
records, for each one, whether it stayed inside the token's workspace.

Developed as an Ariadne extension, it only watches objects flow past.
It deliberately doesn't interact with them, it just saves what happens for
visualization and information.
"""

from logging import getLogger
from typing import NamedTuple
from uuid import UUID

from ariadne.types import Extension, Resolver
from django.db.models import Model
from graphql import GraphQLResolveInfo

from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.workspaces.models import (
    TokenScopeVerdict,
    Workspace,
    WorkspaceTokenUsage,
)

logger = getLogger(__name__)


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

# Reaching another workspace *only* through these is legitimate by design:
# templates are published across workspaces.
TEMPLATE_MODELS = frozenset({"PipelineTemplate", "PipelineTemplateVersion"})

# Past this many distinct objects a request stops remembering which ones it has
# already seen, so the per-object bookkeeping cannot grow with the response. The
# verdict is deliberately not capped: attribution keeps running past the cap, or a
# long request would look in scope merely because it was long.
MAX_TRACKED_OBJECTS = 200


def workspace_id_of(obj: Model) -> UUID | None:
    """The workspace an object belongs to"""
    if isinstance(obj, Workspace):
        return obj.id
    return getattr(obj, "workspace_id", None)


def reachable_datasets(workspace: Workspace, dataset_ids: set) -> dict:
    """External datasets that a member of ``workspace`` legitimately reaches.

    Org-shared datasets and dataset links are reachable for workspace-scoped tokens;
    both survive scoping, so a request using them is not misuse.
    """
    if not dataset_ids:
        return {}

    linked = set(
        DatasetLink.objects.filter(
            workspace_id=workspace.id, dataset_id__in=dataset_ids
        ).values_list("dataset_id", flat=True)
    )
    reasons = {}
    for dataset_id, dataset_workspace_id, shared, organization_id in (
        Dataset.objects.filter(pk__in=dataset_ids)
        .exclude(workspace_id=workspace.id)
        .values_list(
            "id",
            "workspace_id",
            "shared_with_organization",
            "workspace__organization_id",
        )
    ):
        if dataset_id in linked:
            reasons[dataset_workspace_id] = "linked"
        elif shared and organization_id == workspace.organization_id:
            reasons.setdefault(dataset_workspace_id, "org_shared")
    return reasons


def audit_extensions(request, context) -> list:
    """Install the audit only on requests that carry a workspace token.

    Ariadne turns an extension into GraphQL middleware for the whole request, so
    an unconditional one would add a frame to every field resolution of every
    session-authenticated request as well, for nothing.
    """
    if getattr(request, "workspace_token", None) is None:
        return []
    return [WorkspaceScopeAudit]


class WorkspaceScopeAudit(Extension):
    """Records how far each workspace-token-authenticated request reached."""

    def __init__(self):
        self.token = None
        self.root_fields = []
        self.models_by_workspace = {}
        self.dataset_ids = set()
        self.pending = {model: set() for model in INDIRECT_OWNERS}
        self.seen = set()

    def request_started(self, context) -> None:
        self.token = getattr(context["request"], "workspace_token", None)

    def resolve(self, next_: Resolver, obj, info: GraphQLResolveInfo, **kwargs):
        if self.token is not None:
            self._observe(obj, info)
        return next_(obj, info, **kwargs)

    def request_finished(self, context) -> None:
        if self.token is None:
            return
        try:
            self._record(context["request"])
        except Exception:  # never let instrumentation break a request
            logger.exception("workspace token audit failed")

    def _observe(self, obj, info: GraphQLResolveInfo) -> None:
        if info.path.prev is None and info.field_name not in self.root_fields:
            self.root_fields.append(info.field_name)

        if not isinstance(obj, Model):
            return
        key = (type(obj).__name__, obj.pk)
        if key in self.seen:
            return
        if len(self.seen) < MAX_TRACKED_OBJECTS:
            self.seen.add(key)

        for model, owner in INDIRECT_OWNERS.items():
            if isinstance(obj, model):
                if (parent_id := getattr(obj, owner.fk, None)) is not None:
                    self.pending[model].add(parent_id)
                return

        workspace_id = workspace_id_of(obj)
        if workspace_id is None:
            return
        self.models_by_workspace.setdefault(workspace_id, set()).add(type(obj).__name__)
        if isinstance(obj, Dataset):
            self.dataset_ids.add(obj.pk)
        elif (dataset_id := getattr(obj, "dataset_id", None)) is not None:
            # A dataset link reached from another workspace is classified by the
            # dataset it points at, not by the link itself.
            self.dataset_ids.add(dataset_id)

    def _resolve_pending(self) -> None:
        for model, owner in INDIRECT_OWNERS.items():
            parent_ids = self.pending[model]
            if not parent_ids:
                continue
            for workspace_id, dataset_id in owner.parent._base_manager.filter(
                pk__in=parent_ids
            ).values_list(owner.workspace_path, owner.dataset_path):
                if workspace_id is None:
                    continue
                self.models_by_workspace.setdefault(workspace_id, set()).add(
                    model.__name__
                )
                self.dataset_ids.add(dataset_id)

    def _classify(self) -> tuple[str, dict]:
        foreign = {
            workspace_id: models
            for workspace_id, models in self.models_by_workspace.items()
            if workspace_id != self.token.workspace.id
        }
        if not foreign:
            return TokenScopeVerdict.IN_SCOPE, {}

        dataset_reasons = reachable_datasets(self.token.workspace, self.dataset_ids)
        reasons = {}
        for workspace_id, models in foreign.items():
            reason = dataset_reasons.get(workspace_id)
            if reason is None and models <= TEMPLATE_MODELS:
                reason = "template"
            reasons[str(workspace_id)] = reason or "none"

        verdict = (
            TokenScopeVerdict.OUT_OF_SCOPE
            if "none" in reasons.values()
            else TokenScopeVerdict.CROSS_REACHABLE
        )
        return verdict, reasons

    def _record(self, request) -> None:
        self._resolve_pending()
        verdict, foreign_workspaces = self._classify()

        WorkspaceTokenUsage.objects.create(
            token_fingerprint=self.token.fingerprint,
            token_type=self.token.TYPE,
            user=self.token.user,
            workspace=self.token.workspace,
            verdict=verdict,
            root_fields=self.root_fields,
            foreign_workspaces=foreign_workspaces,
            client=request.headers.get("User-Agent", ""),
            ip=request.META.get("REMOTE_ADDR"),
        )

        if verdict == TokenScopeVerdict.OUT_OF_SCOPE:
            # Kept below Sentry's ERROR threshold on purpose: this is expected traffic,
            # but it's good to keep it documented and in mind
            logger.warning(
                "workspace token used outside its workspace",
                extra={
                    "token_fingerprint": self.token.fingerprint,
                    "workspace": self.token.workspace.slug,
                    "root_fields": self.root_fields,
                    "foreign_workspaces": foreign_workspaces,
                },
            )
