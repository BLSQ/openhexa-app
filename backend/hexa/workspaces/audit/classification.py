"""Whether reaching a workspace outside the token's own is legitimate."""

from uuid import UUID

from hexa.datasets.models import Dataset, DatasetLink
from hexa.workspaces.models import TokenScopeVerdict, Workspace

# Reaching another workspace *only* through these is legitimate by design:
# templates are published across workspaces.
TEMPLATE_MODELS = frozenset({"PipelineTemplate", "PipelineTemplateVersion"})


def reachable_datasets(workspace: Workspace, dataset_ids: set) -> dict:
    """External datasets that a ``workspace`` member legitimately reaches.

    Org-shared datasets and dataset links are reachable for workspace-scoped tokens;
    both inside scope, so a request using them is not misuse.
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


def classify(
    token_workspace: Workspace,
    models_by_workspace: dict[UUID, set[str]],
    dataset_ids: set,
) -> tuple[str, dict]:
    """The verdict for a request, plus why each foreign workspace was reached."""
    foreign = {
        workspace_id: models
        for workspace_id, models in models_by_workspace.items()
        if workspace_id != token_workspace.id
    }
    if not foreign:
        return TokenScopeVerdict.IN_SCOPE, {}

    dataset_reasons = reachable_datasets(token_workspace, dataset_ids)
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
