from __future__ import annotations

import enum
import json
import typing
import uuid
from datetime import datetime
from enum import Enum
from functools import cache
from logging import getLogger
from time import sleep
from urllib.parse import quote_plus, urljoin

import django.apps
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from django.db import models, transaction
from django.db.models import OuterRef, Prefetch, Q, Subquery
from django.http import HttpRequest
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import Datasource
from hexa.core.models import Base, WithStatus
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.behaviors import Status
from hexa.core.models.cryptography import EncryptedTextField
from hexa.pipelines.models import Environment, Index, IndexableMixin
from hexa.pipelines.sync import EnvironmentSyncResult
from hexa.plugins.connector_airflow.api import AirflowAPIClient, AirflowAPIError
from hexa.user_management.models import Permission, Team, User

logger = getLogger(__name__)


class ExternalType(Enum):
    CLUSTER = "cluster"
    DAG = "dag"


class ClusterQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        # Clusters are only visible to superusers for now
        return self._filter_for_user_and_query_object(user, Q(pk=None))


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
        dag_runs_info = client.list_dag_runs("~", limit)
        for run_info in dag_runs_info:
            try:
                dag_run = DAGRun.objects.get(
                    dag__dag_id=run_info["dag_id"],
                    run_id=run_info["dag_run_id"],
                )
            except DAGRun.DoesNotExist:
                continue

            dag_run.update_state(run_info)

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
                elif variables[var_name] != json.dumps(config, indent=2):
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

                if dag_info["is_active"] is False:
                    logger.error("DAG %s inactive in airflow", hexa_dag.dag_id)

                if dag_info["is_paused"] is True:
                    client.unpause_dag(dag_id)

                # update runs
                dag_runs_data = client.list_dag_runs(dag_id, get_all=True)

                # Delete runs not in Airflow
                run_ids = [x["dag_run_id"] for x in dag_runs_data]
                DAGRun.objects.filter(dag=hexa_dag).exclude(run_id__in=run_ids)
                # Do not delete them, AccessMod dag_run cannot be deleted
                # orphans.delete()

                for run_info in dag_runs_data:
                    run, created = DAGRun.objects.get_or_create(
                        dag=hexa_dag,
                        run_id=run_info["dag_run_id"],
                        defaults={
                            "execution_date": parse_datetime(run_info["execution_date"])
                        },
                    )
                    run.update_state(run_info)

                    if run.run_logs == "":
                        run.get_run_logs()
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
    sample_config = models.JSONField(blank=True, default=dict)

    def build_dag_config(self):
        return [dag.build_dag_config() for dag in self.dag_set.all()]

    def __str__(self):
        return self.code


class DAGQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            Q(dagpermission__team__in=Team.objects.filter_for_user(user)),
        )


class DAG(IndexableMixin, models.Model):
    class Meta:
        verbose_name = "DAG"
        ordering = ["dag_id"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    indexes = GenericRelation("pipelines.Index")

    template = models.ForeignKey(DAGTemplate, on_delete=models.CASCADE)
    dag_id = models.CharField(max_length=200)

    form_code = models.CharField(max_length=200, null=True, blank=True)

    # for scheduled DAG:
    config = models.JSONField(blank=True, default=dict)
    schedule = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(
        "user_management.User", null=True, blank=False, on_delete=models.SET_NULL
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

    def get_airflow_url(self):
        return f"{self.template.cluster.url}graph?dag_id={self.dag_id}"

    @property
    def last_run(self) -> DAGRun:
        return self.dagrun_set.first()

    def run(
        self,
        *,
        request: HttpRequest,
        conf: typing.Mapping[str, typing.Any] = None,
        webhook_path: str = None,
    ):
        return self.common_run(
            user=request.user,
            run_type=DAGRunTrigger.MANUAL,
            conf=conf,
            webhook_path=webhook_path,
        )

    def run_scheduled(self):
        self.common_run(user=self.user, run_type=DAGRunTrigger.SCHEDULED)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.build_index()

    def get_token(self):
        return Signer().sign_object(
            {
                "id": str(self.id),
                "model": self._meta.model_name,
                "app_label": self._meta.app_label,
            }
        )

    def common_run(
        self,
        user: User,
        run_type: DAGRunTrigger,
        conf: typing.Mapping[str, typing.Any] = None,
        webhook_path: str = None,
    ):
        if conf is None:
            conf = {}

        client = self.template.cluster.get_api_client()
        # add report email to feedback user
        # in case a DAG was created without a user assigned to it
        if user:
            conf["_report_email"] = user.email

        if webhook_path is None:
            webhook_path = reverse("connector_airflow:webhook")
        raw_token, signed_token = self.build_webhook_token()
        conf["_webhook_token"] = signed_token
        conf["_webhook_url"] = f"{settings.BASE_URL}{webhook_path}"

        dag_run_data = client.trigger_dag_run(self.dag_id, run_type=run_type, conf=conf)

        # don't save private information in past run, like email, tokens...
        public_conf = {k: v for k, v in conf.items() if not k.startswith("_")}

        return DAGRun.objects.create(
            dag=self,
            user=user,
            run_id=dag_run_data["dag_run_id"],
            execution_date=parse_datetime(dag_run_data["execution_date"]),
            state=DAGRunState.QUEUED,
            conf=public_conf,
            webhook_token=raw_token,
        )

    def build_dag_config(self):
        return {
            "dag_id": self.dag_id,
            "token": self.get_token(),
            "credentials_url": f'{settings.BASE_URL}{reverse("pipelines:credentials")}',
            "static_config": self.config,
            "report_email": self.user.email if self.user else None,
            "schedule": None,
        }

    @staticmethod
    def build_webhook_token() -> tuple[str, typing.Any]:
        unsigned = str(uuid.uuid4())

        return unsigned, Signer().sign_object(unsigned)


@cache
def limit_data_source_types():
    all_models = django.apps.apps.get_models()
    datasources = [x for x in all_models if issubclass(x, Datasource)]
    names = [x.__name__.lower() for x in datasources]
    return {"model__in": names}


class DAGAuthorizedDatasource(Base):
    dag = models.ForeignKey(
        "DAG", on_delete=models.CASCADE, related_name="authorized_datasources"
    )
    datasource_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=limit_data_source_types,
    )
    datasource_id = models.UUIDField()
    datasource = GenericForeignKey("datasource_type", "datasource_id")
    slug = models.SlugField(
        max_length=200,
        blank=True,
        null=True,
        help_text="A slug to identify the datasource in the pipeline. "
        "If left empty, the datasource will be available with the same name as in the notebooks",
    )  # blank and null needed to allow for multiple empty slugs per dag
    # https://docs.djangoproject.com/en/4.0/ref/models/fields/#django.db.models.Field.null

    class Meta:
        unique_together = [
            ("dag", "slug"),
        ]

    def __str__(self):
        return f'Access to "{self.datasource}" ({self.datasource._meta.verbose_name}) for DAG "{self.dag}"'


class DAGPermission(Permission):
    class Meta(Permission.Meta):
        constraints = [
            models.UniqueConstraint(
                "team",
                "dag",
                name="dag_unique_team",
                condition=Q(team__isnull=False),
            ),
            models.UniqueConstraint(
                "user",
                "dag",
                name="dag_unique_user",
                condition=Q(user__isnull=False),
            ),
            models.CheckConstraint(
                check=Q(team__isnull=False) | Q(user__isnull=False),
                name="dag_user_or_team_not_null",
            ),
        ]

    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)

    def index_object(self) -> None:
        self.dag.build_index()

    def __str__(self) -> str:
        return f"Permission for team '{self.team}' for dag '{self.dag}'"


class DAGRunQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self.filter(dag__in=DAG.objects.filter_for_user(user))

    def filter_for_refresh(self):
        return self.filter(state__in=[DAGRunState.RUNNING, DAGRunState.QUEUED])

    def with_favorite(self, user: User):
        return self.prefetch_related(
            Prefetch(
                "dagrunfavorite_set",
                queryset=DAGRunFavorite.objects.filter_for_user(user),
            )
        ).annotate(
            favorite=Subquery(
                DAGRunFavorite.objects.filter_for_user(user)
                .filter(
                    dag_run=OuterRef("id"),
                )
                .values("name")[:1]
            ),
        )


class DAGRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")
    QUEUED = "queued", _("Queued")
    TERMINATING = "terminating", _("terminating")  # terminating
    STOPPED = "stopped", _("Stopped")


class DAGRunTrigger(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    MANUAL = "MANUAL"


class DAGRun(Base, WithStatus):
    STATUS_MAPPINGS = {
        DAGRunState.SUCCESS: Status.SUCCESS,
        DAGRunState.RUNNING: Status.RUNNING,
        DAGRunState.FAILED: Status.ERROR,
        DAGRunState.QUEUED: Status.PENDING,
        DAGRunState.STOPPED: Status.STOPPED,
        DAGRunState.TERMINATING: Status.TERMINATING,
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
    duration = models.DurationField(null=True)
    conf = models.JSONField(blank=True, default=dict)
    webhook_token = models.CharField(max_length=200, blank=True)
    messages = models.JSONField(null=True, blank=True, default=list)
    outputs = models.JSONField(null=True, blank=True, default=list)
    run_logs = models.TextField(null=True, blank=True)
    current_progress = models.PositiveSmallIntegerField(default=0)

    objects = DAGRunQuerySet.as_manager()

    @property
    def trigger_mode(self):
        if self.run_id.startswith("manual"):
            return DAGRunTrigger.MANUAL
        if self.run_id.startswith("scheduled"):
            return DAGRunTrigger.SCHEDULED

    def get_airflow_url(self):
        return f"{self.dag.template.cluster.url}graph?dag_id={self.dag.dag_id}&execution_date={quote_plus(self.execution_date.isoformat())}"

    def refresh(self) -> None:
        client = self.dag.template.cluster.get_api_client()
        run_data = client.get_dag_run(self.dag.dag_id, self.run_id)

        self.update_state(run_data)

    def update_state(self, run_data):
        should_update = self.state != run_data["state"] or self.state in [
            DAGRunState.RUNNING,
            DAGRunState.QUEUED,
        ]
        if should_update:
            self.last_refreshed_at = timezone.now()
            self.state = run_data["state"]
            if run_data["end_date"]:
                self.duration = (
                    parse_datetime(run_data["end_date"]) - self.execution_date
                )
            success_or_failed = run_data["state"] in [
                DAGRunState.SUCCESS,
                DAGRunState.FAILED,
            ]
            if success_or_failed:
                self.current_progress = 100
                self.get_run_logs()
            self.save()

    def add_to_favorites(self, *, user: User, name: str) -> DAGRunFavorite:
        if self.is_in_favorites(user):
            raise ValueError("DAGRun is already in favorites")

        return DAGRunFavorite.objects.create(user=user, dag_run=self, name=name)

    def remove_from_favorites(self, user: User):
        if not self.is_in_favorites(user):
            raise ValueError("DAGRun is not in favorites")

        DAGRunFavorite.objects.get(user=user, dag_run=self).delete()

    def is_in_favorites(self, user: User):
        try:
            DAGRunFavorite.objects.get(dag_run=self, user=user)
            return True
        except DAGRunFavorite.DoesNotExist:
            return False

    def log_message(self, priority: str, message: str):
        self.messages.append(
            {
                "priority": priority if priority else "info",
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.save()

    def set_output(self, title: str, uri: str):
        self.outputs.append({"title": title, "uri": uri})
        self.save()

    def progress_update(self, percent: int):
        self.current_progress = percent
        self.save()

    def get_run_logs(self):
        client = self.dag.template.cluster.get_api_client()
        tasks = client.list_task_instances(dag_id=self.dag.dag_id, run_id=self.run_id)[
            "task_instances"
        ]
        logs = ""
        for task in tasks:
            if (
                task["task_id"] != "success"
                and task["task_id"] != "failure"
                and task["state"] != "skipped"
            ):
                log = client.get_logs(
                    dag_id=self.dag.dag_id, run_id=self.run_id, task=task["task_id"]
                )
                logs = logs + log + "\n\n\n"
        self.run_logs = logs

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.state]
        except KeyError:
            return Status.UNKNOWN


class DAGRunFavoriteQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            Q(user=user),
            return_all_if_superuser=False,
        )


class DAGRunFavorite(Base):
    class Meta:
        unique_together = [("user", "dag_run")]

    user = models.ForeignKey("user_management.User", on_delete=models.CASCADE)
    dag_run = models.ForeignKey("DAGRun", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    objects = DAGRunFavoriteQuerySet.as_manager()
