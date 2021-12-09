import typing
from enum import Enum
from urllib.parse import urljoin

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.core.models import Base, Permission, WithStatus
from hexa.core.models.cryptography import EncryptedTextField
from hexa.pipelines.models import Environment, Index, Pipeline, PipelinesQuerySet
from hexa.pipelines.sync import EnvironmentSyncResult
from hexa.plugins.connector_airflow.api import AirflowAPIClient, AirflowAPIError
from hexa.user_management.models import User


class ExternalType(Enum):
    CLUSTER = "cluster"
    DAG = "dag"


class ClusterQuerySet(PipelinesQuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            clusterpermission__team__in=[t.pk for t in user.team_set.all()]
        ).distinct()


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
        identical_count = 0  # TODO: handle identical?
        with transaction.atomic():
            client = self.get_api_client()
            dags_data = client.list_dags()

            # Delete dags not in Airflow
            dag_ids = [x["dag_id"] for x in dags_data["dags"]]
            orphans = DAG.objects.filter(cluster=self).exclude(dag_id__in=dag_ids)
            dag_orphans_count = orphans.count()
            orphans.delete()

            # Update or create the others
            for dag_info in dags_data["dags"]:
                dag, created = DAG.objects.get_or_create(
                    cluster=self, dag_id=dag_info["dag_id"]
                )
                dag.description = dag_info["description"]
                dag.save()
                if created:
                    created_count += 1
                else:
                    updated_count += 1

                dag_runs_data = client.list_dag_runs(dag.dag_id)

                # Delete runs not in Airflow
                run_ids = [x["dag_run_id"] for x in dag_runs_data["dag_runs"]]
                orphans = DAGRun.objects.filter(dag=dag).exclude(run_id__in=run_ids)
                run_orphans_count = orphans.count()
                orphans.delete()

                for run_info in dag_runs_data["dag_runs"]:
                    run, created = DAGRun.objects.get_or_create(
                        dag=dag,
                        run_id=run_info["dag_run_id"],
                        defaults={"execution_date": run_info["execution_date"]},
                    )
                    run.last_refreshed_at = timezone.now()
                    run.state = run_info["state"]
                    run.save()
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return EnvironmentSyncResult(
            environment=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            orphaned=dag_orphans_count + run_orphans_count,
        )

    def get_api_client(self):
        return AirflowAPIClient(
            url=self.api_url, username=self.username, password=self.password
        )

    def clean(self):
        client = self.get_api_client()
        try:
            client.list_dags()
        except AirflowAPIError as e:
            raise ValidationError(f"Error connecting to Airflow: {e}")


class ClusterPermission(Permission):
    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("cluster", "team")]

    def index_object(self) -> None:
        self.cluster.build_index()

    def __str__(self) -> str:
        return f"Permission for team '{self.team}' on cluster '{self.cluster}'"


class DAGQuerySet(PipelinesQuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(cluster__in=Cluster.objects.filter_for_user(user))


class DAG(Pipeline):
    class Meta:
        verbose_name = "DAG"
        ordering = ["dag_id"]

    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE)
    dag_id = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sample_config = models.JSONField(default=dict, blank=True)

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
        # index.search = f"{self.name}"

    def get_absolute_url(self) -> str:
        return reverse(
            "connector_airflow:dag_detail",  # TODO
            args=(self.cluster.id, self.id),
        )

    @property
    def last_run(self) -> "DAGRun":
        return self.dagrun_set.first()

    def run(self, *, user: User, conf: typing.Mapping[str, typing.Any] = None):
        client = self.cluster.get_api_client()
        dag_run_data = client.trigger_dag_run(self.dag_id, conf=conf)

        return DAGRun.objects.create(
            dag=self,
            user=user,
            run_id=dag_run_data["dag_run_id"],
            execution_date=dag_run_data["execution_date"],
            state=DAGRunState.QUEUED,
            conf=conf,
        )


class DAGRunQuerySet(PipelinesQuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(dag__in=DAG.objects.filter_for_user(user))

    def filter_for_refresh(self):
        return self.filter(state__in=[DAGRunState.RUNNING, DAGRunState.QUEUED])


class DAGRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")
    QUEUED = "queued", _("Queued")


class DAGRun(Base, WithStatus):
    STATUS_MAPPINGS = {
        DAGRunState.SUCCESS: WithStatus.SUCCESS,
        DAGRunState.RUNNING: WithStatus.RUNNING,
        DAGRunState.FAILED: WithStatus.ERROR,
        DAGRunState.QUEUED: WithStatus.PENDING,
    }

    class Meta:
        ordering = ("-execution_date",)

    user = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)
    last_refreshed_at = models.DateTimeField(null=True)
    run_id = models.CharField(max_length=200, blank=False)
    execution_date = models.DateTimeField()
    state = models.CharField(max_length=200, blank=False, choices=DAGRunState.choices)
    conf = models.JSONField(default=dict, blank=True)

    objects = DAGRunQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse(
            "connector_airflow:dag_run_detail",
            args=(self.dag.cluster.id, self.dag.id, self.id),
        )

    def refresh(self) -> None:
        client = self.dag.cluster.get_api_client()
        run_data = client.get_dag_run(self.dag.dag_id, self.run_id)

        self.last_refreshed_at = timezone.now()
        self.state = run_data["state"]
        self.save()

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.state]
        except KeyError:
            return WithStatus.UNKNOWN
