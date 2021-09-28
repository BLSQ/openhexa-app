from dataclasses import dataclass
from enum import Enum
from urllib.parse import urljoin

import requests
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.models import Base, Permission, WithStatus
from hexa.core.models.cryptography import EncryptedTextField
from hexa.pipelines.models import Environment, Index, Pipeline
from hexa.user_management.models import User


class ExternalType(Enum):
    CLUSTER = "cluster"
    DAG = "dag"


class ClusterQuerySet(models.QuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            clusterpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Cluster(Environment):
    class Meta:
        ordering = ("name",)
        verbose_name = "Airflow Cluster"

    name = models.CharField(max_length=200)
    url = models.URLField(blank=False)

    username = EncryptedTextField()
    password = EncryptedTextField()

    objects = ClusterQuerySet.as_manager()

    @property
    def api_url(self):
        return urljoin(self.url, "api/v1/")

    def __str__(self) -> str:
        return self.name

    def get_permission_set(self):
        return self.clusterpermission_set.all()

    def populate_index(self, index: Index) -> None:  # TODO
        index.external_name = self.name
        index.external_type = ExternalType.CLUSTER.value
        index.path = [self.id.hex]
        index.external_id = f"{self.api_url}"
        index.content = self.content_summary
        index.search = f"{self.name}"

    def get_absolute_url(self) -> str:
        return reverse(
            "connector_airflow:cluster_detail",
            args=(self.id,),
        )

    @property
    def content_summary(self) -> str:
        count = self.dag_set.count()

        return (
            ""
            if count == 0
            else _("%(dag_count)d DAG%(suffix)s")
            % {"dag_count": count, "suffix": pluralize(count)}
        )

    def sync(self):
        created_count = 0
        updated_count = 0
        identical_count = 0
        with transaction.atomic():
            session = self.get_api_session()
            url = urljoin(self.api_url, "dags")
            response = session.get(url)
            # TODO: handle non-200
            response_data = response.json()

            # Delete dags not in Airflow
            airflow_ids = [x["dag_id"] for x in response_data["dags"]]
            orphans = DAG.objects.filter(cluster=self).exclude(dag_id__in=airflow_ids)
            new_orphans_count = orphans.count()
            orphans.delete()

            # Update or create the others
            for dag_info in response_data["dags"]:
                dag, created = DAG.objects.get_or_create(
                    cluster=self, dag_id=dag_info["dag_id"]
                )
                dag.description = dag_info["description"]
                dag.save()
                if created:
                    created_count += 1
                else:
                    updated_count += 1

                url = urljoin(
                    self.api_url, f"dags/{dag.dag_id}/dagRuns?order_by=-end_date"
                )
                response = session.get(url)
                for run_info in response.json()["dag_runs"]:
                    run, _ = DAGRun.objects.get_or_create(
                        dag=dag,
                        run_id=run_info["dag_run_id"],
                        defaults={"execution_date": run_info["execution_date"]},
                    )
                    run.last_refreshed_at = timezone.now()
                    run.state = run_info["state"]
                    run.save()

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return DatasourceSyncResult(
            datasource=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            orphaned=new_orphans_count,
        )

    def get_api_session(self):
        session = requests.Session()
        session.auth = (self.username, self.password)
        return session

    def clean(self):
        session = self.get_api_session()
        try:
            response = session.get(urljoin(self.url, "api/v1/dags"))
            if not response.ok:
                raise ValidationError(
                    f"Error connecting to Airflow: error {response.status_code}"
                )
        except Exception as e:
            raise ValidationError(f"Error connecting to Airflow: {e}")


class ClusterPermission(Permission):
    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("cluster", "team")]

    def index_object(self) -> None:
        self.cluster.build_index()

    def __str__(self) -> str:
        return f"Permission for team '{self.team}' on cluster '{self.cluster}'"


class DAGQuerySet(models.QuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            cluster__clusterpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class DAG(Pipeline):
    class Meta:
        verbose_name = "DAG"
        ordering = ["dag_id"]

    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE)
    dag_id = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    objects = DAGQuerySet.as_manager()

    def __str__(self) -> str:
        return self.dag_id

    def get_permission_set(self):
        return self.cluster.clusterpermission_set.all()

    def populate_index(self, index: Index):
        # index.external_name = self.name  # TODO
        index.external_type = ExternalType.DAG.value
        index.path = [self.cluster.id.hex, self.id.hex]
        index.external_id = f"{self.dag_id}"
        index.content = self.content_summary
        # index.search = f"{self.name}"

    def get_absolute_url(self) -> str:
        return reverse(
            "connector_airflow:dag_detail",  # TODO
            args=(self.cluster.id, self.id),
        )

    @property
    def content_summary(self) -> str:
        count = self.dagconfig_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d DAG configuration%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    @property
    def last_run(self) -> "DAGRun":
        return self.dagrun_set.first()

    def run(self):
        session = self.cluster.get_api_session()

        url = urljoin(self.cluster.api_url, f"dags/{self.dag_id}/dagRuns")
        response = session.post(
            url, json={"execution_date": timezone.now().isoformat()}
        )
        # TODO: handle non-200
        response_data = response.json()

        return DAGRun.objects.create(
            dag=self,
            run_id=response_data["dag_run_id"],
            execution_date=response_data["execution_date"],
            state=DAGRunState.RUNNING,
        )


class DAGConfigQuerySet(models.QuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dag__cluster__clusterpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )


class DAGConfig(Base):
    class Meta:
        verbose_name = "DAG config"

    name = models.CharField(max_length=200)
    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)
    config_data = models.JSONField(default=dict)

    objects = DAGConfigQuerySet.as_manager()

    @property
    def content_summary(self) -> str:
        count = self.dagrun_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d DAG configuration%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    @property
    def last_run(self) -> "DAGRun":
        return DAGRun.objects.get_last_for_dag_and_config(dag_config=self)


@dataclass
class DAGRunResult:
    dag_config: DAGConfig
    # TODO: document and move in api module

    def __str__(self) -> str:
        return _('The DAG config "%(name)s" has been run') % {
            "name": self.dag_config.display_name
        }


class DAGRunQuerySet(models.QuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dag_config__dag__cluster__clusterpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )

    def get_last_for_dag_and_config(
        self, *, dag: DAG = None, dag_config: DAGConfig = None
    ):
        qs = self.all()
        if dag is not None:
            qs = qs.filter(dag_config__dag=dag)
        if dag_config is not None:
            qs = qs.filter(dag_config=dag_config)

        return qs.order_by("-airflow_execution_date").first()


class DAGRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")


class DAGRun(Base, WithStatus):
    STATUS_MAPPINGS = {
        DAGRunState.SUCCESS: WithStatus.SUCCESS,
        DAGRunState.RUNNING: WithStatus.PENDING,
        DAGRunState.FAILED: WithStatus.ERROR,
    }

    class Meta:
        ordering = ("-execution_date",)

    dag_config = models.ForeignKey(
        "DAGConfig", on_delete=models.CASCADE, null=True, blank=True
    )
    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)
    last_refreshed_at = models.DateTimeField(null=True)
    run_id = models.CharField(max_length=200, blank=False)
    message = models.TextField()
    execution_date = models.DateTimeField()
    state = models.CharField(max_length=200, blank=False, choices=DAGRunState.choices)

    objects = DAGRunQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse(
            "connector_airflow:dag_run_detail",
            args=(self.dag.cluster.id, self.dag.id, self.id),
        )

    def refresh(self) -> None:
        session = self.dag.cluster.get_api_session()
        url = urljoin(
            self.dag.cluster.api_url,
            f"dags/{self.dag.dag_id}/dagRuns/{self.run_id}",
        )

        response = session.get(url)
        # TODO: handle non-200
        response_data = response.json()

        self.last_refreshed_at = timezone.now()
        self.state = response_data["state"]
        self.save()

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.airflow_state]
        except KeyError:
            return WithStatus.UNKNOWN
