import json
from urllib.parse import quote_plus

from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRun
from hexa.ui.datacard import (
    Action,
    CodeProperty,
    Datacard,
    DateProperty,
    Section,
    StatusProperty,
    TextProperty,
    URLProperty,
)


class ClusterSection(Section):
    title = "Airflow Data"

    name = TextProperty(text="name", translate=False)
    url = URLProperty(url="web_url")


class ClusterCard(Datacard):
    title = "name"
    subtitle = "generic_description"
    image_src = "_image_src"

    external = ClusterSection()
    metadata = OpenHexaMetaDataSection(value="index")

    actions = [Action(label="Sync", url="get_sync_url", icon="refresh")]

    def get_sync_url(self, cluster: Cluster):
        return reverse(
            "pipelines:environment_sync",
            kwargs={
                "environment_id": cluster.id,
                "environment_contenttype_id": ContentType.objects.get_for_model(
                    Cluster
                ).id,
            },
        )

    @property
    def generic_description(self) -> str:
        return _("Airflow Cluster")

    @property
    def _image_src(self) -> str:
        return static("connector_airflow/img/symbol.svg")


class DAGSection(Section):
    title = "Airflow Data"

    dag_id = TextProperty(text="dag_id", label="Identifier", translate=False)
    description = TextProperty(text="description", markdown=True)


class DAGCard(Datacard):
    title = "dag_id"
    subtitle = "generic_description"
    image_src = "_image_src"

    external = DAGSection()
    metadata = OpenHexaMetaDataSection(value="index")

    actions = [
        Action(
            label="Open in Airflow",
            url="get_airflow_url",
            icon="external_link",
            method="GET",
            primary=False,
            open_in_new_tab=True,
            enabled_when=lambda r: r.user.is_superuser,
        ),
        Action(label="Configure & run", url="get_run_url", icon="play", method="GET"),
    ]

    @staticmethod
    def get_run_url(dag: DAG):
        return reverse(
            "connector_airflow:dag_run_create",
            kwargs={
                "cluster_id": dag.cluster.id,
                "dag_id": dag.id,
            },
        )

    @staticmethod
    def get_airflow_url(dag: DAG):
        return f"{dag.cluster.url}graph?dag_id={dag.dag_id}"

    @property
    def generic_description(self) -> str:
        return _("Airflow DAG")

    @property
    def _image_src(self) -> str:
        return static("connector_airflow/img/symbol.svg")


class DAGRunSection(Section):
    title = "Airflow Data"

    run_id = TextProperty(text="run_id", label="Identifier", translate=False)
    dag = URLProperty(url="get_dag_url", text="dag.dag_id", label="DAG", external=False)
    execution_date = DateProperty(date="execution_date", label="Execution Date")
    user = TextProperty(text="user.display_name")
    state = StatusProperty(value="status", label="State")
    config = CodeProperty(code="get_conf_as_string", label="Config", language="json")

    @staticmethod
    def get_dag_url(run: DAGRun):
        return reverse(
            "connector_airflow:dag_detail",
            kwargs={
                "cluster_id": run.dag.cluster.id,
                "dag_id": run.dag.id,
            },
        )

    @staticmethod
    def get_conf_as_string(run: DAGRun):
        return json.dumps(run.conf, indent=2)


class DAGRunCard(Datacard):
    title = "run_id"
    subtitle = "generic_description"
    image_src = "_image_src"
    actions = [
        Action(
            label="Open in Airflow",
            url="get_airflow_url",
            icon="external_link",
            method="GET",
            primary=False,
            open_in_new_tab=True,
            enabled_when=lambda r: r.user.is_superuser,
        ),
        Action(
            label="Configure and re-run", url="get_clone_url", icon="play", method="GET"
        ),
    ]

    external = DAGRunSection()

    @property
    def generic_description(self) -> str:
        return _("Airflow DAG run")

    @property
    def _image_src(self) -> str:
        return static("connector_airflow/img/symbol.svg")

    @staticmethod
    def get_clone_url(run: DAGRun):
        return (
            reverse(
                "connector_airflow:dag_run_create",
                kwargs={
                    "cluster_id": run.dag.cluster.id,
                    "dag_id": run.dag.id,
                },
            )
            + f"?conf_from={run.id}"
        )

    @staticmethod
    def get_airflow_url(run: DAGRun):
        return f"{run.dag.cluster.url}graph?dag_id={run.dag.dag_id}&execution_date={quote_plus(run.execution_date.isoformat())}"
