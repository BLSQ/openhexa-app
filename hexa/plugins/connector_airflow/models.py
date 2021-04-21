import json
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from hexa.catalog.models import Content
from hexa.common.models import Base
from hexa.pipelines.models import (
    Environment as BaseEnvironment,
    PipelineIndex,
    PipelineIndexPermission,
)


class CredentialsQuerySet(models.QuerySet):
    def get_for_team(self, user):
        # TODO: root credentials concept?
        if user.is_active and user.is_superuser:
            return self.get(team=None)

        if user.team_set.count() == 0:
            raise Credentials.DoesNotExist()

        return self.get(team=user.team_set.first().pk)  # TODO: multiple teams?


class Credentials(Base):
    """This class is a temporary way to store GCP Airflow credentials. This approach is not safe for production,
    as credentials are not encrypted.
    TODO: Store credentials in a secure storage engine like Vault.
    TODO: Handle different kind of credentials (not just OIDC)
    """

    class Meta:
        verbose_name_plural = "Credentials"
        ordering = ("service_account_email",)

    # TODO: unique?
    team = models.ForeignKey(
        "user_management.Team",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="airflow_credential_set",
    )
    service_account_email = models.EmailField()
    service_account_key_data = models.JSONField()
    oidc_target_audience = models.CharField(max_length=200, blank=False)

    objects = CredentialsQuerySet.as_manager()

    def __str__(self):
        return self.service_account_email


class EnvironmentQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            environmentpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Environment(BaseEnvironment):
    class Meta:
        ordering = ("hexa_name",)

    name = models.CharField(max_length=200)
    url = models.URLField(blank=False)
    api_url = models.URLField()
    api_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )

    objects = EnvironmentQuerySet.as_manager()

    def index(self):
        pipeline_index = PipelineIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.hexa_owner,
            name=self.name,
            countries=self.hexa_countries,
            content_summary=self.content_summary,  # TODO: why?
            last_synced_at=self.hexa_last_synced_at,
            detail_url=reverse("connector_airflow:environment_detail", args=(self.pk,)),
        )

        for permission in self.environmentpermission_set.all():
            PipelineIndexPermission.objects.create(
                catalog_index=pipeline_index, team=permission.team
            )

    @property
    def content_summary(self):
        if self.hexa_last_synced_at is None:
            return ""

        return _("%(dag_count)s DAGs") % {
            "dag_count": self.dag_set.count(),
        }

    def __str__(self):
        return self.name


class EnvironmentPermission(Base):
    airflow_environment = models.ForeignKey("Environment", on_delete=models.CASCADE)
    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)


class DAGQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            environment_environmentpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )


class DAG(Base):
    class Meta:
        verbose_name = "DAG"
        ordering = ["dag_id"]

    environment = models.ForeignKey("Environment", on_delete=models.CASCADE)
    dag_id = models.CharField(max_length=200, blank=False)

    objects = DAGQuerySet.as_manager()

    @property
    def display_name(self):
        return self.dag_id


class DAGConfigQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dag_environment_environmentpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )


class DAGConfig(Base):
    class Meta:
        verbose_name = "DAG config"

    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    config_data = models.JSONField(default=dict)
    last_run_at = models.DateTimeField(null=True, blank=True)

    objects = DAGConfigQuerySet.as_manager()

    def run(self):
        # See https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf
        # and https://google-auth.readthedocs.io/en/latest/user-guide.html#identity-tokens
        credentials = service_account.IDTokenCredentials.from_service_account_info(
            self.dag.environment.api_credentials.service_account_key_data,
            target_audience=self.dag.environment.api_credentials.oidc_target_audience,
        )
        session = AuthorizedSession(credentials)

        response = session.post(
            f"{self.dag.environment.api_url.rstrip('/')}/dags/{self.dag.dag_id}/dag_runs",
            data=json.dumps(self.config_data),
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        response_data = response.json()

        self.last_run_at = timezone.now()
        self.save()

        return DAGConfigRunResult(self)


class DAGConfigRunResult:
    # TODO: document and move

    def __init__(self, dag_config):
        self.dag_config = dag_config

    def __str__(self):
        # figures = (
        #     f"{self.created} new, {self.updated} updated, {self.identical} unaffected"
        # )

        return f'The DAG config "{self.dag_config.name}" has been run'
