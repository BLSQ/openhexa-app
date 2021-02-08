from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base import Content


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


class DatasourceType(models.TextChoices):
    DHIS2 = "DHIS2", _("DHIS2")
    IASO = "IASO", _("Iaso")
    FILES = "FILES", _("Files")


class Datasource(Content):
    class NoConnection(Exception):
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
        """Sync the datasource using its connection"""

        try:
            sync_result = self.connection.sync()
            self.last_synced_at = timezone.now()
            self.save()

            return sync_result
        except ObjectDoesNotExist:
            raise Datasource.NoConnection(
                f'The datasource "{self.display_name}" has no connection'
            )

    @property
    def content_summary(self):
        try:
            return self.connection.get_content_summary()
        except ObjectDoesNotExist:
            return None

    @property
    def just_synced(self):
        return (
            self.last_synced_at is not None
            and (timezone.now() - self.last_synced_at).seconds < 60
        )
