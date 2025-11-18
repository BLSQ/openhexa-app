from ariadne import QueryType
from django.db.models import Q
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.tags.models import InvalidTag, Tag
from hexa.workspaces.models import Workspace

pipeline_template_query = QueryType()


@pipeline_template_query.field("pipelineTemplates")
def resolve_pipeline_templates(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    search = kwargs.get("search", "")

    pipeline_templates = (
        PipelineTemplate.objects.select_related("workspace", "source_pipeline")
        .prefetch_related("tags")
        .with_pipelines_count()
        .filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(tags__name__icontains=search)
            | Q(functional_type__icontains=search)
        )
        .distinct()
    )

    if kwargs.get("functional_type"):
        pipeline_templates = pipeline_templates.filter(
            functional_type=kwargs.get("functional_type")
        )

    workspace_slug = kwargs.get("workspace_slug")
    workspace = None
    if workspace_slug:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
        pipeline_templates = pipeline_templates.filter(workspace=workspace)

    tags = kwargs.get("tags", [])
    if tags:
        try:
            tag_objects = Tag.from_names(tags)
            if workspace:
                tag_objects = tag_objects.filter(
                    pipeline_templates__workspace__organization=workspace.organization
                ).distinct()
            pipeline_templates = pipeline_templates.filter_by_tags(tag_objects)
        except InvalidTag:
            pipeline_templates = PipelineTemplate.objects.none()

    only_validated = kwargs.get("only_validated")
    if only_validated is not None:
        if only_validated:
            # Show only validated templates (validatedAt is not null)
            pipeline_templates = pipeline_templates.filter(validated_at__isnull=False)
        else:
            # Show only unvalidated/community templates (validatedAt is null)
            pipeline_templates = pipeline_templates.filter(validated_at__isnull=True)

    order_by = kwargs.get("order_by")
    if order_by:
        base_field = order_by.lstrip("-")

        if base_field in PipelineTemplate.UNIQUE_SORT_FIELDS:
            pipeline_templates = pipeline_templates.order_by(order_by, "id")
        else:
            pipeline_templates = pipeline_templates.order_by(order_by, "name", "id")
    else:
        pipeline_templates = pipeline_templates.order_by(
            *PipelineTemplate.default_order_by()
        )

    return result_page(
        pipeline_templates,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@pipeline_template_query.field("templateByCode")
def resolve_template_by_code(_, info, **kwargs):
    try:
        template = PipelineTemplate.objects.get(code=kwargs["code"])
    except PipelineTemplate.DoesNotExist:
        template = None
    return template


@pipeline_template_query.field("pipelineTemplateVersion")
def resolve_pipeline_template_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        version = PipelineTemplateVersion.objects.filter_for_user(request.user).get(
            id=kwargs["id"]
        )
        return version
    except PipelineTemplateVersion.DoesNotExist:
        return None


bindables = [
    pipeline_template_query,
]
