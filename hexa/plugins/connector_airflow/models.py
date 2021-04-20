from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from google.oauth2 import service_account
import requests

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
        verbose_name = "Airflow Credentials"
        verbose_name_plural = "Airflow Credentials"
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
    service_account_key = models.JSONField()
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
        verbose_name = "GCP Composer environment"
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

    def sync(self):
        credentials = service_account.IDTokenCredentials.from_service_account_info(
            self.api_credentials.service_account_key,
            target_audience=self.api_credentials.oidc_target_audience,
        )

        response = requests.get(
            self.api_url.rstrip("/") + "/dags/",
            headers={"Authorization": f"Bearer {credentials}"},
        )
        response_data = response.json()

        return response_data

    @property
    def content_summary(self):
        if self.hexa_last_synced_at is None:
            return ""

        return _("%(object_count)s objects") % {
            "object_count": self.object_set.count(),
        }

    def __str__(self):
        return self.name


class EnvironmentPermission(Base):
    airflow_environment = models.ForeignKey("Environment", on_delete=models.CASCADE)
    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)


# class DAG(Content):
#     class Meta:
#         verbose_name = "Airflow DAG"
#         ordering = ["name"]
#
#     environment = models.ForeignKey("Environment", on_delete=models.CASCADE)
#     key = models.TextField()
#     size = models.PositiveBigIntegerField()
#     storage_class = models.CharField(max_length=200)  # TODO: choices
#     type = models.CharField(max_length=200)  # TODO: choices
#     name = models.CharField(max_length=200)
#     last_modified = models.DateTimeField(null=True)
#
#     @property
#     def display_name(self):
#         return self.name
#
#     def index(self):
#         pass  # TODO: implement
