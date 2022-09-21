import pathlib

from ariadne import EnumType, MutationType, ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.countries.models import Country

from .models import DAG, DAGRun

dags_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

dag_run_order_by_enum = EnumType(
    "DAGRunOrderBy",
    {
        "EXECUTION_DATE_DESC": "-execution_date",
        "EXECUTION_DATE_ASC": "execution_date",
    },
)

dag_run_status_enum = EnumType("DAGRunStatus", DAGRun.STATUS_MAPPINGS)

dag_object = ObjectType("DAG")

dag_object.set_alias("externalId", "dag_id")


@dag_object.field("template")
def resolve_dag_template(dag: DAG, info, **kwargs):
    return dag.template


@dag_object.field("user")
def resolve_dag_user(dag: DAG, info, **kwargs):
    return dag.user


@dag_object.field("externalUrl")
def resolve_dag_external_url(dag: DAG, info, **kwargs):
    return dag.get_airflow_url()


@dag_object.field("label")
def resolve_dag_label(dag: DAG, info, **kwargs):
    return dag.index.label


@dag_object.field("countries")
def resolve_dag_countries(dag: DAG, info, **kwargs):
    return dag.index.countries


@dag_object.field("description")
def resolve_dag_description(dag: DAG, info, **kwargs):
    return dag.index.description


@dag_object.field("tags")
def resolve_dag_tags(dag: DAG, info, **kwargs):
    return dag.index.tags.all()


@dag_object.field("runs")
def resolve_dag_runs(dag: DAG, info, **kwargs):
    qs = dag.dagrun_set.all()

    order_by = kwargs.get("orderBy", None)
    if order_by is not None:
        qs = qs.order_by(order_by)

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


dag_run_object = ObjectType("DAGRun")


@dag_run_object.field("user")
def resolve_dag_run_user(run: DAGRun, info, **kwargs):
    return run.user


@dag_run_object.field("externalId")
def resolve_dag_run_id(run: DAGRun, info, **kwargs):
    return run.run_id


@dag_run_object.field("externalUrl")
def resolve_dag_run_external_url(run: DAGRun, info, **kwargs):
    return run.get_airflow_url()


@dag_run_object.field("duration")
def resolve_dag_run_duration(run: DAGRun, info, **kwargs):
    return int(run.duration.total_seconds()) if run.duration is not None else 0


@dag_run_object.field("config")
def resolve_dag_run_config(run: DAGRun, info, **kwargs):
    return run.conf


dag_run_object.set_alias("progress", "current_progress")
dag_run_object.set_alias("logs", "run_logs")


dags_query = QueryType()


@dags_query.field("dags")
def resolve_dags(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    qs = DAG.objects.filter_for_user(request.user)

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@dags_query.field("dag")
def resolve_dag(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    return DAG.objects.filter_for_user(request.user).get(id=kwargs.get("id"))


@dags_query.field("dagRun")
def resolve_dag_run(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    return DAGRun.objects.filter_for_user(request.user).get(id=kwargs.get("id"))


dags_mutations = MutationType()


@dags_mutations.field("runDAG")
def resolve_run_dag(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        dag: DAG = DAG.objects.filter_for_user(request.user).get(id=input.get("dagId"))
        dag_run = dag.run(request=request, conf=input.get("config"))

        return {"dag": dag, "dag_run": dag_run, "success": True, "errors": []}
    except DAG.DoesNotExist:
        return {
            "success": False,
            "errors": ["DAG_NOT_FOUND"],
        }


@dags_mutations.field("updateDAG")
def resolve_update_dag(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        dag: DAG = DAG.objects.filter_for_user(request.user).get(id=input.get("id"))
        if input.get("schedule", None) is not None:
            dag.schedule = input["schedule"]
        for key in ["label", "description"]:
            if input.get(key, None) is not None:
                setattr(dag.index, key, input[key])

        countries = (
            [Country.objects.get(code=c["code"]) for c in input["countries"]]
            if "countries" in input
            else None
        )
        if countries is not None:
            dag.index.countries = countries
        dag.index.save()
        dag.save()
        return {"success": True, "errors": [], "dag": dag}

    except DAG.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}


dags_bindables = [
    dags_query,
    dags_mutations,
    dag_object,
    dag_run_object,
    dag_run_status_enum,
    dag_run_order_by_enum,
]
