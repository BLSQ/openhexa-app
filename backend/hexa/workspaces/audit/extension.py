"""The Ariadne extension that watches a token-authenticated request go by."""

from logging import getLogger

from ariadne.types import Extension, Resolver
from graphql import GraphQLResolveInfo

from hexa.workspaces.models import TokenScopeVerdict, WorkspaceTokenUsage

from .attribution import INDIRECT_OWNERS, resolve_indirect_owners, tracking_plan
from .classification import classify

logger = getLogger(__name__)

_NOTHING = object()


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
        # GraphQL resolves all the selected fields of one object back to back, so the
        # object of the previous call is nearly always the object of this one.
        self.last_obj = _NOTHING

    def request_started(self, context) -> None:
        self.token = context["request"].workspace_token

    def resolve(self, next_: Resolver, obj, info: GraphQLResolveInfo, **kwargs):
        if info.path.prev is None:
            self.root_fields.setdefault(info.field_name, None)
        if obj is not self.last_obj:
            self.last_obj = obj
            self._observe(obj)
        return next_(obj, info, **kwargs)

    def request_finished(self, context) -> None:
        try:
            self._record(context["request"])
        except Exception:  # never let instrumentation break a request
            logger.exception("workspace token audit failed")

    def _observe(self, obj) -> None:
        """Called once per object rather than once per field, and kept allocation-free.

        Every accumulator is a set, so re-observing an object is harmless; nothing here
        needs to remember which objects it has already seen.
        """
        plan = tracking_plan(type(obj))
        if plan is None:
            return

        if plan.owner is not None:
            parent_id = getattr(obj, plan.owner.fk, None)
            if parent_id is not None:
                self.pending[plan.tracked_as].add(parent_id)
            return

        workspace_id = getattr(obj, plan.workspace_attr, None)
        if workspace_id is None:
            return
        self._attribute(workspace_id, plan.name)
        if plan.dataset_attr is not None:
            dataset_id = getattr(obj, plan.dataset_attr, None)
            if dataset_id is not None:
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
