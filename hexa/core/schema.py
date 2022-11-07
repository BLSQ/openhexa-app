import pathlib

from ariadne import ObjectType, QueryType, load_schema_from_path
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy

from hexa.app import get_hexa_app_configs
from hexa.catalog.models import Index
from hexa.core.activities import Activity, ActivityList
from hexa.core.models.behaviors import Status
from hexa.plugins.connector_airflow.models import DAG
from hexa.plugins.connector_s3.models import Object

core_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)


core_activity_object = ObjectType("Activity")
core_queries = QueryType()


@core_queries.field("lastActivities")
def resolve_core_dashboard_last_activities(coreDashboard, info, **kwargs):
    request = info.context["request"]
    last_activities = ActivityList(
        [
            Activity(
                occurred_at=timezone.now().replace(hour=0, minute=0),
                description=gettext_lazy("All datasources are up to date!"),
                status=Status.SUCCESS.name,
                url=reverse("catalog:index"),
            )
        ]
    )
    for app_config in get_hexa_app_configs(connector_only=True):
        last_activities += app_config.get_last_activities(request)

    return last_activities


@core_queries.field("datasources")
def resolve_core_dashboard_datasource(_, info, **kwargs):
    request = info.context["request"]
    datasources = Index.objects.filter_for_user(request.user).roots().count()

    return datasources


@core_queries.field("totalNotebooks")
def resolve_core_dashboard_notebooks(_, info, **kwargs):
    request = info.context["request"]

    totalNotebooks = (
        Object.objects.filter(key__iendswith=".ipynb")
        .filter_for_user(request.user)
        .count()
    )
    return totalNotebooks


@core_queries.field("pipelines")
def resolve_core_dashboard_pipelines(_, info, **kwargs):
    request = info.context["request"]
    return DAG.objects.filter_for_user(request.user).count()


core_bindables = [core_activity_object, core_queries]
