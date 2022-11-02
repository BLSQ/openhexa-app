import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest
from django.urls import reverse

from hexa.core.graphql import result_page
from hexa.countries.models import Country

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


dashboard_mutations = MutationType()


@dashboard_mutations.field("updateExternalDashboard")
def resolve_update_external_dashboard(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        dashboard: ExternalDashboard = ExternalDashboard.objects.filter_for_user(
            request.user
        ).get(id=input.get("id"))
        index = dashboard.index
        if input.get("name", None):
            index.label = input["name"]
        if input.get("description", None):
            index.description = input["description"]

        countries = (
            [Country.objects.get(code=c["code"]) for c in input["countries"]]
            if "countries" in input
            else None
        )
        if countries is not None:
            index.countries = countries
        index.save()
        dashboard.save()
        return {"success": True, "errors": [], "external_dashboard": dashboard}
    except ExternalDashboard.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}


dashboards_bindables = [dashboard_queries, dashboard_object, dashboard_mutations]
