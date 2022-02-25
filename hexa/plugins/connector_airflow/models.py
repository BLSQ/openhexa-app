import json
import typing
import uuid
from base64 import b64encode
from enum import Enum
from logging import getLogger
from time import sleep
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.core.models import Base, Permission, WithStatus
from hexa.core.models.behaviors import Status
from hexa.core.models.cryptography import EncryptedTextField
from hexa.pipelines.models import Environment, Index, Pipeline, PipelinesQuerySet
from hexa.pipelines.sync import EnvironmentSyncResult
from hexa.plugins.connector_airflow.api import AirflowAPIClient, AirflowAPIError
from hexa.user_management.models import User

logger = getLogger(__name__)


class ExternalType(Enum):
    CLUSTER = "cluster"
    DAG = "dag"


class ClusterQuerySet(PipelinesQuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self
        else:
            return self.none()


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

    def get_permission_set(self):
        return []

    @property
    def dag_set(self):
        return DAG.objects.filter(template__cluster=self)

    @property
    def content_summary(self) -> str:
        count = DAG.objects.filter(template__cluster=self).count()

        return (
            ""
            if count == 0
            else _("%(dag_count)d DAG%(suffix)s")
            % {"dag_count": count, "suffix": pluralize(count)}
        )

    def dag_runs_sync(self, limit: int = 100):
        """
        Sync the last few dag run, to maintain the state of the most recent one up to date
        Try to minimise the DB update -> only refresh when state is different or dag is "active"

        :param limit: number of dag runs to track, starting from the most recent one
        :return: None
        """
        client = self.get_api_client()
        dag_runs = client.list_dag_runs("~", limit)
        for run_info in dag_runs["dag_runs"]:
            try:
                dag_run = DAGRun.objects.get(
                    dag__dag_id=run_info["dag_id"],
                    run_id=run_info["dag_run_id"],
                )
            except DAGRun.DoesNotExist:
                continue
            if dag_run.state != run_info["state"] or dag_run.state in (
                DAGRunState.RUNNING,
                DAGRunState.QUEUED,
            ):
                dag_run.last_refreshed_at = timezone.now()
                dag_run.state = run_info["state"]
                dag_run.save()

    def sync(self):
        created_count = 0
        updated_count = 0
        identical_count = 0
        orphans_count = 0

        with transaction.atomic():
            client = self.get_api_client()

            # update variables
            variables = client.list_variables()
            for template in self.dagtemplate_set.all():
                var_name = f"TEMPLATE_{template.code.upper()}_DAGS"
                config = template.build_dag_config()
                if var_name not in variables:
                    client.create_variable(var_name, json.dumps(config, indent=2))
                    created_count += 1
                elif variables[var_name] != config:
                    client.update_variable(var_name, json.dumps(config, indent=2))
                    updated_count += 1
                else:
                    identical_count += 1

            if created_count or updated_count:
                # let's wait to airflow to reload dags -- can take up to 60s
                # it isn't a problem: edition is rare and sync is async
                # just don't lock the DB when doing cluster.sync
                sleep(settings.AIRFLOW_SYNC_WAIT)

            # check import error
            # refresh dags and check if conform to target
            dags_data = client.list_dags()

            # do we have more dags that airflow?
            airflow_dags = set([x["dag_id"] for x in dags_data["dags"]])
            hexa_dags = set(
                [x.dag_id for x in DAG.objects.filter(template__cluster=self)]
            )
            for hexa_orphan in hexa_dags - airflow_dags:
                logger.error(
                    "DAG %s present in hexa and not in airflow -> configuration issue",
                    hexa_orphan,
                )
            for airflow_orphan in airflow_dags - hexa_dags:
                logger.error(
                    "DAG %s present in airflow and not in hexa -> configuration issue",
                    airflow_orphan,
                )
            orphans_count += len(airflow_dags - hexa_dags)
            orphans_count += len(hexa_dags - airflow_dags)

            # for common dags: download dag run
            for dag_id in set.intersection(airflow_dags, hexa_dags):
                hexa_dag = DAG.objects.get(template__cluster=self, dag_id=dag_id)
                dag_info = [d for d in dags_data["dags"] if d["dag_id"] == dag_id][0]

                # update dag info
                hexa_dag.template.description = dag_info["description"]
                hexa_dag.template.save()

                # check schedule
                if not (
                    (
                        dag_info["schedule_interval"] is None
                        and hexa_dag.schedule is None
                    )
                    or (
                        dag_info["schedule_interval"]
                        and dag_info["schedule_interval"]["value"] == hexa_dag.schedule
                    )
                ):
                    logger.error(
                        "DAG %s schedule missmatch between openhexa/airflow",
                        hexa_dag.dag_id,
                    )
                if dag_info["is_active"] is False or dag_info["is_paused"] is True:
                    logger.error("DAG %s inactive in airflow", hexa_dag.dag_id)

                # update runs
                dag_runs_data = client.list_dag_runs(dag_id)

                # Delete runs not in Airflow
                run_ids = [x["dag_run_id"] for x in dag_runs_data["dag_runs"]]
                orphans = DAGRun.objects.filter(dag=hexa_dag).exclude(
                    run_id__in=run_ids
                )
                orphans.delete()

                for run_info in dag_runs_data["dag_runs"]:
                    run, created = DAGRun.objects.get_or_create(
                        dag=hexa_dag,
                        run_id=run_info["dag_run_id"],
                        defaults={"execution_date": run_info["execution_date"]},
                    )
                    run.last_refreshed_at = timezone.now()
                    run.state = run_info["state"]
                    run.save()

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return EnvironmentSyncResult(
            environment=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            orphaned=orphans_count,
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


class DAGTemplate(Base):
    class Meta:
        verbose_name = "DAGTemplate"
        ordering = ["code"]

    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE)
    code = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sample_config = models.JSONField(default=dict, blank=True)

    def build_dag_config(self):
        return [dag.build_dag_config() for dag in self.dag_set.all()]

    def __str__(self):
        return self.code


class DAGQuerySet(PipelinesQuerySet):
    def filter_for_user(self, user: User):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dagpermission__team__in=[t.pk for t in user.team_set.all()]
        ).distinct()


class DAG(Pipeline):
    class Meta:
        verbose_name = "DAG"
        ordering = ["dag_id"]

    template = models.ForeignKey(DAGTemplate, on_delete=models.CASCADE)
    dag_id = models.CharField(max_length=200)

    # for scheduled DAG:
    config = models.JSONField(default=dict, blank=True)
    schedule = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(
        "user_management.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    objects = DAGQuerySet.as_manager()

    def __str__(self) -> str:
        return self.dag_id

    def get_permission_set(self):
        return self.dagpermission_set.all()

    def populate_index(self, index: Index):
        index.external_name = self.dag_id
        index.external_type = ExternalType.DAG.value
        index.path = [self.template.cluster.id.hex, self.id.hex]
        index.external_id = f"{self.dag_id}"
        index.search = f"{self.dag_id}"

    def get_absolute_url(self) -> str:
        return reverse(
            "connector_airflow:dag_detail",  # TODO
            args=(self.id,),
        )

    @property
    def last_run(self) -> "DAGRun":
        return self.dagrun_set.first()

    def run(self, *, user: User, conf: typing.Mapping[str, typing.Any] = None):
        if conf is None:
            conf = {}

        client = self.template.cluster.get_api_client()
        # add report email to feedback user
        conf["_report_email"] = user.email
        dag_run_data = client.trigger_dag_run(self.dag_id, conf=conf)

        return DAGRun.objects.create(
            dag=self,
            user=user,
            run_id=dag_run_data["dag_run_id"],
            execution_date=dag_run_data["execution_date"],
            state=DAGRunState.QUEUED,
            conf=conf,
            webhook_token=uuid.uuid4(),
        )

    def build_dag_config(self):
        credentials = []
        for ds in self.authorized_datasources.all():
            credential = ds.datasource.get_pipeline_credentials()
            credential["label"] = ds.label
            credentials.append(credential)
        return {
            "dag_id": self.dag_id,
            "credentials": credentials,
            "static_config": self.config,
            "report_email": self.user.email if self.user else None,
            "schedule": self.schedule if self.schedule else None,
        }


class DAGAuthorizedDatasource(Base):
    dag = models.ForeignKey(
        "DAG", on_delete=models.CASCADE, related_name="authorized_datasources"
    )
    datasource_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    datasource_id = models.UUIDField()
    datasource = GenericForeignKey("datasource_type", "datasource_id")
    label = models.CharField(max_length=200, default="datasource")


class DAGPermission(Permission):
    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("dag", "team")]

    def index_object(self) -> None:
        self.dag.build_index()

    def __str__(self) -> str:
        return f"Permission for team '{self.team}' for dag '{self.dag}'"


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
        DAGRunState.SUCCESS: Status.SUCCESS,
        DAGRunState.RUNNING: Status.RUNNING,
        DAGRunState.FAILED: Status.ERROR,
        DAGRunState.QUEUED: Status.PENDING,
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
    webhook_token = models.CharField(max_length=200, blank=True)

    objects = DAGRunQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse(
            "connector_airflow:dag_run_detail",
            args=(self.dag.id, self.id),
        )

    def refresh(self) -> None:
        client = self.dag.template.cluster.get_api_client()
        run_data = client.get_dag_run(self.dag.dag_id, self.run_id)

        self.last_refreshed_at = timezone.now()
        self.state = run_data["state"]

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.state]
        except KeyError:
            return Status.UNKNOWN

    def sign_webhook_token(self):
        return b64encode(Signer().sign(self.webhook_token).encode("utf-8")).decode(
            "utf-8"
        )
