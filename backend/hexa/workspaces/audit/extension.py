"""The Ariadne extension that watches a token-authenticated request go by."""

from logging import getLogger

from ariadne.types import Extension, Resolver
from django.db.models import Model
from graphql import GraphQLResolveInfo

from hexa.datasets.models import Dataset
from hexa.workspaces.models import TokenScopeVerdict, WorkspaceTokenUsage

from .attribution import INDIRECT_OWNERS, resolve_indirect_owners, workspace_id_of
from .classification import classify

logger = getLogger(__name__)

# Past this many distinct objects a request stops remembering which ones it has
# already seen, so ``seen`` cannot grow with the response.
# Attribution keeps running past the cap. What it accumulates stays bounded by the
# distinct workspaces and datasets touched.
MAX_TRACKED_OBJECTS = 200


def audit_extensions(request, context) -> list:
    """Install the audit only on requests that carry a workspace token.

    Ariadne turns an extension into GraphQL middleware for the whole request,
    so we avoid adding it to every request that doesn't need it.
    """
    if getattr(request, "workspace_token", None) is None:
        return []
    return [WorkspaceScopeAudit]


class WorkspaceScopeAudit(Extension):
    """Records how far each workspace-token-authenticated request reached."""

    def __init__(self):
        self.token = None
        # A dict, not a set, to keep the fields in the order the query asked for them.
        self.root_fields: dict[str, None] = {}
        self.models_by_workspace = {}
        self.dataset_ids = set()
        self.pending = {model: set() for model in INDIRECT_OWNERS}
        self.seen = set()

    def request_started(self, context) -> None:
        self.token = context["request"].workspace_token

    def resolve(self, next_: Resolver, obj, info: GraphQLResolveInfo, **kwargs):
        self._observe(obj, info)
        return next_(obj, info, **kwargs)

    def request_finished(self, context) -> None:
        try:
            self._record(context["request"])
        except Exception:  # never let instrumentation break a request
            logger.exception("workspace token audit failed")

    def _observe(self, obj, info: GraphQLResolveInfo) -> None:
        if info.path.prev is None:
            self.root_fields.setdefault(info.field_name, None)

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
        self._attribute(workspace_id, type(obj).__name__)
        if isinstance(obj, Dataset):
            self.dataset_ids.add(obj.pk)
        elif (dataset_id := getattr(obj, "dataset_id", None)) is not None:
            # A dataset link reached from another workspace is classified by the
            # dataset it points at, not by the link itself.
            self.dataset_ids.add(dataset_id)

    def _attribute(self, workspace_id, model_name: str) -> None:
        self.models_by_workspace.setdefault(workspace_id, set()).add(model_name)

    def _record(self, request) -> None:
        for workspace_id, model_name, dataset_id in resolve_indirect_owners(
            self.pending
        ):
            self._attribute(workspace_id, model_name)
            self.dataset_ids.add(dataset_id)

        verdict, foreign_workspaces = classify(
            self.token.workspace, self.models_by_workspace, self.dataset_ids
        )

        WorkspaceTokenUsage.objects.create(
            token_fingerprint=self.token.fingerprint,
            token_type=self.token.TYPE,
            user=self.token.user,
            workspace=self.token.workspace,
            verdict=verdict,
            root_fields=list(self.root_fields),
            foreign_workspaces=foreign_workspaces,
            client=request.headers.get("User-Agent", ""),
            ip=request.META.get("REMOTE_ADDR"),
        )

        if verdict == TokenScopeVerdict.OUT_OF_SCOPE:
            # Kept below Sentry's ERROR threshold on purpose: this is expected traffic,
            # but it's good to keep it documented
            logger.warning(
                "workspace token used outside its workspace",
                extra={
                    "token_fingerprint": self.token.fingerprint,
                    "workspace": self.token.workspace.slug,
                    "root_fields": list(self.root_fields),
                    "foreign_workspaces": foreign_workspaces,
                },
            )
