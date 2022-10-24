import pathlib

from ariadne import ObjectType, QueryType, load_schema_from_path
from django.urls import reverse

from hexa.core.graphql import result_page

from .models import ExternalDashboard

dashboards_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)


dashboard_object = ObjectType("ExternalDashboard")


@dashboard_object.field("countries")
def resolve_dashboard_countries(dashboard, info, **kwargs):
    return dashboard.index.countries


@dashboard_object.field("tags")
def resolve_dashboard_tags(dashboard, info, **kwargs):
    return dashboard.index.tags.all()


@dashboard_object.field("name")
def resolve_dashboard_name(dashboard, info, **kwargs):
    return dashboard.index.display_name


@dashboard_object.field("description")
def resolve_dashboard_description(dashboard, info, **kwargs):
    return dashboard.index.description


@dashboard_object.field("pictureUrl")
def resolve_dashboard_picture_url(dashboard, info, **kwargs):
    return reverse(
        "visualizations:dashboard_image", kwargs={"dashboard_id": dashboard.id}
    )


dashboard_queries = QueryType()


@dashboard_queries.field("externalDashboards")
def resolve_external_dashboards(_, info, page=1, perPage=15):
    request = info.context["request"]
    queryset = (
        ExternalDashboard.objects.prefetch_indexes()
        .filter_for_user(request.user)
        .order_by("-updated_at")
    )

    return result_page(queryset=queryset, page=page, per_page=perPage)


@dashboard_queries.field("externalDashboard")
def resolve_external_dashboard(_, info, **kwargs):
    request = info.context["request"]
    try:
        return (
            ExternalDashboard.objects.prefetch_indexes()
            .filter_for_user(request.user)
            .get(id=kwargs["id"])
        )
    except ExternalDashboard.DoesNotExist:
        return None


dashboards_bindables = [dashboard_queries, dashboard_object]
