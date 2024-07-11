from ariadne import QueryType, convert_kwargs_to_snake_case

from hexa.core.graphql import result_page

from ..models import (
    Dataset,
    DatasetFileSnapshot,
    DatasetLink,
    DatasetVersion,
)

datasets_queries = QueryType()


@datasets_queries.field("datasets")
@convert_kwargs_to_snake_case
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


@datasets_queries.field("datasetFileSnapshot")
def resolve_dataset_file_snapshot(_, info, **kwargs):
    try:
        if kwargs.get("file_id"):
            return DatasetFileSnapshot.objects.get(
                dataset_version_file=kwargs["file_id"]
            )
        elif kwargs.get("id"):
            return DatasetFileSnapshot.objects.get(id=kwargs["id"])
        else:
            return None
    except DatasetFileSnapshot.DoesNotExist:
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
    try:
        return DatasetLink.objects.filter_for_user(request.user).get(
            dataset__slug=kwargs["datasetSlug"], workspace__slug=kwargs["workspaceSlug"]
        )
    except DatasetLink.DoesNotExist:
        return None


bindables = [datasets_queries]
