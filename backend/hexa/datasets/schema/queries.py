from ariadne import QueryType

from hexa.core.graphql import result_page

from ...workspaces.models import Workspace
from ..models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)

datasets_queries = QueryType()


@datasets_queries.field("datasets")
def resolve_datasets(_, info, query=None, page=1, per_page=15):
    request = info.context["request"]
    qs = Dataset.objects.filter_for_user(request.user).order_by("-updated_at")

    if query is not None:
        qs = qs.filter(name__icontains=query)

    return result_page(queryset=qs, page=page, per_page=per_page)


@datasets_queries.field("dataset")
def resolve_dataset(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Dataset.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Dataset.DoesNotExist:
        return None


@datasets_queries.field("datasetVersion")
def resolve_dataset_version(_, info, **kwargs):
    request = info.context["request"]
    try:
        return DatasetVersion.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except DatasetVersion.DoesNotExist:
        return None


@datasets_queries.field("datasetVersionFile")
def resolve_dataset_version_file(_, info, **kwargs):
    request = info.context["request"]
    try:
        return DatasetVersionFile.objects.filter_for_user(request.user).get(
            id=kwargs["id"]
        )
    except DatasetVersionFile.DoesNotExist:
        return None


@datasets_queries.field("datasetLink")
def resolve_dataset_link(_, info, **kwargs):
    request = info.context["request"]
    try:
        return DatasetLink.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except DatasetLink.DoesNotExist:
        return None


@datasets_queries.field("datasetLinkBySlug")
def resolve_dataset_link_by_slug(_, info, **kwargs):
    request = info.context["request"]
    user_links = DatasetLink.objects.filter_for_user(request.user)
    dataset_slug = kwargs["dataset_slug"]
    workspace_slug = kwargs["workspace_slug"]

    # First: dataset link in the specific workspace
    result = user_links.filter(
        dataset__slug=dataset_slug,
        dataset__workspace__slug=workspace_slug,
        workspace__slug=workspace_slug,
    ).first()
    if result:
        return result

    # Second: dataset shared to the specified workspace
    result = user_links.filter(
        dataset__slug=dataset_slug,
        workspace__slug=workspace_slug,
    ).first()
    if result:
        return result

    # Third: organization shared datasets - ensure workspace is in same org as dataset
    workspace = Workspace.objects.filter(slug=workspace_slug).first()
    if not workspace or not workspace.organization:
        return None
    result = user_links.filter(
        dataset__slug=dataset_slug,
        dataset__shared_with_organization=True,
        dataset__workspace__organization=workspace.organization,
    ).first()
    if result:
        return result

    return None


bindables = [datasets_queries]
