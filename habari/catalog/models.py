from functools import lru_cache

from django.apps import apps
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from habari.common.models import Base, DynamicTextChoices
from habari.plugins.app import HabariPluginAppConfig


class DatasourceType(DynamicTextChoices):
    @staticmethod
    @lru_cache
    def build_choices():
        choices = {}
        for app in apps.get_app_configs():
            if isinstance(app, HabariPluginAppConfig):
                choices = choices | app.get_datasource_types()

        return choices


class Content(Base):
    class Meta:
        abstract = True

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)

    @property
    def display_name(self):
        return self.short_name if self.short_name != "" else self.name

    def __str__(self):
        return self.display_name


class OrganizationType(models.TextChoices):
    CORPORATE = "CORPORATE", _("Corporate")
    ACADEMIC = "ACADEMIC", _("Academic")
    GOVERNMENT = "GOVERNMENT", _("Government")
    NGO = "NGO", _("Non-governmental")


class Organization(Content):
    organization_type = models.CharField(
        choices=OrganizationType.choices, max_length=100
    )
    url = models.URLField(blank=True)
    contact_info = models.TextField(blank=True)

    @property
    def organization_type_label(self):
        return OrganizationType[self.organization_type].label


class Datasource(Content):
    class NoConnector(Exception):
        pass

    owner = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    datasource_type = models.CharField(choices=DatasourceType.choices, max_length=100)
    url = models.URLField(blank=True)
    active_from = models.DateTimeField(null=True, blank=True)
    active_to = models.DateTimeField(null=True, blank=True)
    public = models.BooleanField(default=False, verbose_name="Public dataset")
    last_synced_at = models.DateTimeField(null=True, blank=True)

    @property
    def datasource_type_label(self):
        return DatasourceType[self.datasource_type].label

    def sync(self):
        """Sync the datasource using its connector"""

        try:
            sync_result = self.connector.sync()
            self.last_synced_at = timezone.now()
            self.save()

            return sync_result
        except ObjectDoesNotExist:
            raise Datasource.NoConnector(
                f'The datasource "{self.display_name}" has no connection'
            )

    @property
    def content_summary(self):
        try:
            return self.connector.get_content_summary()
        except ObjectDoesNotExist:
            return None

    @property
    def just_synced(self):
        return (
            self.last_synced_at is not None
            and (timezone.now() - self.last_synced_at).seconds < 60
        )


class Area(Content):
    pass


class Theme(Content):
    pass


class Connector(Base):
    class Meta:
        abstract = True

    datasource = models.OneToOneField(
        "catalog.Datasource", on_delete=models.CASCADE, related_name="connector"
    )


class ExternalContent(Base):
    class Meta:
        abstract = True

    external_id = models.CharField(max_length=100, unique=True)
    datasource = models.ForeignKey(
        "catalog.Datasource",
        on_delete=models.CASCADE,
    )
    area = models.ForeignKey(
        "catalog.Area", null=True, blank=True, on_delete=models.SET_NULL
    )
    theme = models.ForeignKey(
        "catalog.Theme", null=True, blank=True, on_delete=models.SET_NULL
    )

    @property
    def display_name(self):
        raise NotImplementedError(
            f"Every catalog external content class should implement display_name()"
        )

    def __str__(self):
        return self.display_name
