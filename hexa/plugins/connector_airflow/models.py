from dataclasses import dataclass
from enum import Enum

import json
import uuid
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from hexa.core.models import Base, WithStatus, Permission, RichContent
from hexa.core.models.cryptography import EncryptedTextField
from hexa.pipelines.models import (
    Environment,
    Index,
    IndexPermission,
    Pipeline,
)
from hexa.user_management.models import User


class ExternalType(Enum):
    CLUSTER = "cluster"
    DAG = "dag"


class Credentials(Base):
    """This class is a temporary way to store GCP Airflow credentials. This approach is not safe for production,
    as credentials are not encrypted.
    TODO: Store credentials in a secure storage engine like Vault.
    TODO: Handle different kind of credentials (not just OIDC)
    """

    OIDC_TARGET_AUDIENCE_DOC_URL = (
        "https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf"
        "#get_the_client_id_of_the_iam_proxy"
    )
    OIDC_TARGET_AUDIENCE_HELP_TEXT = (
        f'Corresponds to the <a href="{OIDC_TARGET_AUDIENCE_DOC_URL}" target="_blank">'
        f"client_id of the IAM Proxy</a>"
    )

    class Meta:
        verbose_name_plural = "Credentials"
        ordering = ("service_account_email",)

    service_account_email = EncryptedTextField()
    service_account_key_data = EncryptedTextField(
        help_text="The content of the JSON key in GCP"
    )
    oidc_target_audience = models.CharField(
        max_length=200,
        blank=False,
        help_text=OIDC_TARGET_AUDIENCE_HELP_TEXT,
    )

    @property
    def display_name(self) -> str:
        return self.service_account_email


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

    api_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=200)
    web_url = models.URLField(blank=False)
    api_url = models.URLField()

    objects = ClusterQuerySet.as_manager()

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

    def run(self) -> "DAGRunResult":
        # TODO: move in API module
        # See https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf
        # and https://google-auth.readthedocs.io/en/latest/user-guide.html#identity-tokens
        # as well as https://cloud.google.com/composer/docs/samples/composer-get-environment-client-id
        api_credentials = self.dag.cluster.api_credentials
        service_account_key_data = json.loads(api_credentials.service_account_key_data)
        id_token_credentials = (
            service_account.IDTokenCredentials.from_service_account_info(
                service_account_key_data,
                target_audience=api_credentials.oidc_target_audience,
            )
        )
        session = AuthorizedSession(id_token_credentials)
        dag_config_run_id = str(uuid.uuid4())
        api_url = self.dag.cluster.api_url
        response = session.post(
            f"{api_url.rstrip('/')}/dags/{self.dag.dag_id}/dag_runs",
            data=json.dumps(
                {
                    "conf": self.config_data,
                    "run_id": dag_config_run_id,
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        # TODO: handle non-200
        response_data = response.json()

        DAGRun.objects.create(
            id=dag_config_run_id,
            dag_config=self,
            last_refreshed_at=timezone.now(),
            airflow_run_id=response_data["run_id"],
            airflow_execution_date=response_data["execution_date"],
            airflow_message=response_data["message"],
            airflow_state=DAGRunState.RUNNING,
        )

        self.last_run_at = timezone.now()
        self.save()

        return DAGRunResult(self)


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
        ordering = ("-last_refreshed_at",)

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
        # TODO: move in api module
        # See https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf
        # and https://google-auth.readthedocs.io/en/latest/user-guide.html#identity-tokens
        api_credentials = self.dag_config.dag.cluster.api_credentials
        service_account_key_data = json.loads(api_credentials.service_account_key_data)
        id_token_credentials = (
            service_account.IDTokenCredentials.from_service_account_info(
                service_account_key_data,
                target_audience=api_credentials.oidc_target_audience,
            )
        )
        session = AuthorizedSession(id_token_credentials)
        api_url = self.dag_config.dag.cluster.api_url
        execution_date = self.execution_date.isoformat()
        response = session.get(
            f"{api_url.rstrip('/')}/dags/{self.dag_config.dag.dag_id}/dag_runs/{execution_date}",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        # TODO: handle non-200
        response_data = response.json()

        self.last_refreshed_at = timezone.now()
        self.airflow_state = response_data["state"]
        self.save()

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.airflow_state]
        except KeyError:
            return WithStatus.UNKNOWN
