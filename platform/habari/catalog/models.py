import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class Base(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrganizationType(models.TextChoices):
    CORPORATE = "CORPORATE", _("Corporate")
    ACADEMIC = "ACADEMIC", _("Academic")
    GOVERNMENT = "GOVERNMENT", _("Government")


class Organization(Base):
    organization_type = models.CharField(
        choices=OrganizationType.choices, max_length=50
    )
    name = models.TextField(max_length=100)
    country = CountryField()

    def __str__(self):
        return f"{self.name} ({_(OrganizationType[self.organization_type].label)})"


class SourceType(models.TextChoices):
    DHIS2 = "DHIS2", _("DHIS2")
    IASO = "IASO", _("Iaso")
    FILES = "FILES", _("Files")


class DataSource(Base):
    owner = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL
    )
    source_type = models.CharField(choices=SourceType.choices, max_length=50)
    name = models.TextField(max_length=200)
    country = CountryField()
    active_from = models.DateTimeField(null=True, blank=True)
    active_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.owner.name}, {_(SourceType[self.source_type])})"
