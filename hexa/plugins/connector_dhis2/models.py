from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import (
    Datasource,
    Entry,
    CatalogIndex,
    CatalogIndexPermission,
    CatalogIndexType,
)
from hexa.core.models import Base, Permission, RichContent
from .api import Dhis2Client
from .sync import sync_from_dhis2_results
from ...catalog.sync import DatasourceSyncResult
from ...core.date_utils import date_format
from ...core.models.cryptography import EncryptedTextField


class Credentials(Base):
    """This class is a temporary way to store S3 credentials. This approach is not safe for production,
    as credentials are not encrypted.
    """

    class Meta:
        verbose_name = "DHIS2 API Credentials"
        verbose_name_plural = "DHIS2 API Credentials"
        ordering = ("api_url",)

    api_url = models.URLField()
    username = EncryptedTextField()
    password = EncryptedTextField()

    @property
    def display_name(self):
        return self.api_url


class InstanceQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            instancepermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Instance(Datasource):
    class Meta:
        verbose_name = "DHIS2 Instance"
        ordering = ("url",)

    api_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )
    url = models.URLField(blank=True)
    indexes = GenericRelation("catalog.CatalogIndex")

    objects = InstanceQuerySet.as_manager()

    @property
    def display_name(self):
        return self.url

    def sync(self, user):
        """Sync the datasource by querying the DHIS2 API"""

        client = Dhis2Client(
            url=self.api_credentials.api_url,
            username=self.api_credentials.username,
            password=self.api_credentials.password,
        )

        results = DatasourceSyncResult(datasource=self)

        # Sync data elements
        with transaction.atomic():
            for results_batch in client.fetch_data_elements():
                results += sync_from_dhis2_results(
                    model_class=DataElement,
                    instance=self,
                    results=results_batch,
                )

            # Sync indicator types
            for results_batch in client.fetch_indicator_types():
                results += sync_from_dhis2_results(
                    model_class=IndicatorType,
                    instance=self,
                    results=results_batch,
                )

            # Sync indicators
            for results_batch in client.fetch_indicators():
                results += sync_from_dhis2_results(
                    model_class=Indicator,
                    instance=self,
                    results=results_batch,
                )

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return results

    @property
    def content_summary(self):
        de_count = self.dataelement_set.count()
        i_count = self.indicator_set.count()

        return (
            ""
            if de_count == 0 and i_count == 0
            else _("%(count)d item%(suffix)s")
            % {
                "count": de_count + i_count,
                "suffix": pluralize(de_count + i_count),
            }
        )

    def index(self):
        catalog_index, _ = CatalogIndex.objects.update_or_create(
            defaults={
                "last_synced_at": self.last_synced_at,
                "content_summary": self.content_summary,
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            index_type=CatalogIndexType.DATASOURCE,
            detail_url=reverse("connector_dhis2:instance_detail", args=(self.pk,)),
        )
        for permission in self.instancepermission_set.all():
            CatalogIndexPermission.objects.get_or_create(
                catalog_index=catalog_index, team=permission.team
            )


class InstancePermission(Permission):
    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("instance", "team")]

    def index_object(self):
        self.instance.index()

    def __str__(self):
        return f"Permission for team '{self.team}' on instance '{self.instance}'"


class Dhis2Entry(Entry):
    class Meta:
        abstract = True

    instance = models.ForeignKey("Instance", null=False, on_delete=models.CASCADE)
    dhis2_id = models.CharField(max_length=200)
    name = models.TextField()
    short_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    external_access = models.BooleanField()
    favorite = models.BooleanField()
    created = models.DateTimeField()
    last_updated = models.DateTimeField()

    @property
    def display_name(self):
        return self.short_name if self.short_name != "" else self.name

    def update(self, **kwargs):
        for key in {"name", "short_name", "description"} & set(kwargs.keys()):
            setattr(self, key, kwargs[key])

        self.save()


class DomainType(models.TextChoices):
    AGGREGATE = "AGGREGATE", _("Aggregate")
    TRACKER = "TRACKER", _("Tracker")


class ValueType(models.TextChoices):
    TEXT = "TEXT", _("Text")
    LONG_TEXT = "LONG_TEXT", _("Long text")
    LETTER = "LETTER", _("Letter")
    PHONE_NUMBER = "PHONE_NUMBER", _("Phone number")
    EMAIL = "EMAIL", _("Email")
    YES_NO = "YES_NO", _("Yes/No")
    YES_ONLY = "YES_ONLY", _("Yes Only")
    DATE = "DATE", _("Date")
    DATE_AND_TIME = "DATE_AND_TIME", _("Date & Time")
    TIME = "TIME", _("Time")
    NUMBER = "NUMBER", _("Number")
    UNIT_INTERVAL = "UNIT_INTERVAL", _("Unit interval")
    PERCENTAGE = "PERCENTAGE", _("Percentage")
    INTEGER = "INTEGER", _("Integer")
    INTEGER_POSITIVE = "INTEGER_POSITIVE", _("Positive Integer")
    INTEGER_NEGATIVE = "INTEGER_NEGATIVE", _("Negative Integer")
    INTEGER_ZERO_OR_POSITIVE = "INTEGER_ZERO_OR_POSITIVE", _("Positive or Zero Integer")
    TRACKER_ASSOCIATE = "TRACKER_ASSOCIATE", _("Tracker Associate")
    USERNAME = "USERNAME", _("Username")
    COORDINATE = "COORDINATE", _("Coordinate")
    ORGANISATION_UNIT = "ORGANISATION_UNIT", _("Organisation Unit")
    AGE = "AGE", _("Age")
    URL = "URL", _("URL")
    FILE = "FILE", _("File")
    IMAGE = "IMAGE", _("Image")


class AggregationType(models.TextChoices):
    AVERAGE = "AVERAGE", _("Average")
    AVERAGE_SUM_ORG_UNIT = "AVERAGE_SUM_ORG_UNIT ", _("Average sum for org unit")
    COUNT = "COUNT", _("Count")
    CUSTOM = "CUSTOM", _("Custom")
    DEFAULT = "DEFAULT", _("Default")
    LAST = "LAST", _("Last")
    LAST_AVERAGE_ORG_UNIT = "LAST_AVERAGE_ORG_UNIT", _("Last average for org unit")
    MAX = "MAX", _("Max")
    MIN = "MIN", _("Min")
    NONE = "NONE", _("None")
    STDDEV = "STDDEV", _("Standard Deviation")
    SUM = "SUM", _("Sum")
    VARIANCE = "VARIANCE", _("Variance")


class DataElement(Dhis2Entry):
    class Meta:
        verbose_name = "DHIS2 Data Element"
        ordering = ("name",)

    code = models.CharField(max_length=100, blank=True)
    domain_type = models.CharField(choices=DomainType.choices, max_length=100)
    value_type = models.CharField(choices=ValueType.choices, max_length=100)
    aggregation_type = models.CharField(choices=AggregationType.choices, max_length=100)

    def index(self):
        catalog_index, _ = CatalogIndex.objects.update_or_create(
            defaults={
                "last_synced_at": self.instance.last_synced_at,
                "external_name": self.name,
                "external_short_name": self.short_name,
                "external_description": self.description,
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            index_type=CatalogIndexType.CONTENT,
            parent=CatalogIndex.objects.get(object_id=self.instance.id),
            detail_url=reverse(
                "connector_dhis2:data_element_detail",
                args=(self.instance.pk, self.pk),
            ),
        )

        for permission in self.instance.instancepermission_set.all():
            CatalogIndexPermission.objects.get_or_create(
                catalog_index=catalog_index, team=permission.team
            )


class IndicatorType(Dhis2Entry):
    class Meta:
        verbose_name = "DHIS2 Indicator type"
        ordering = ("name",)

    number = models.BooleanField()
    factor = models.IntegerField()

    def index(self):  # TODO: fishy
        pass


class Indicator(Dhis2Entry):
    class Meta:
        verbose_name = "DHIS2 Indicator"
        ordering = ("name",)

    code = models.CharField(max_length=100, blank=True)
    indicator_type = models.ForeignKey(
        "IndicatorType", null=True, on_delete=models.SET_NULL
    )
    annualized = models.BooleanField()

    def index(self):
        catalog_index, _ = CatalogIndex.objects.update_or_create(
            defaults={
                "last_synced_at": self.instance.last_synced_at,
                "external_name": self.name,
                "external_short_name": self.short_name,
                "external_description": self.description,
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            index_type=CatalogIndexType.CONTENT,
            parent=CatalogIndex.objects.get(object_id=self.instance.id),
            detail_url=reverse(
                "connector_dhis2:indicator_detail",
                args=(self.instance.pk, self.pk),
            ),
        )

        for permission in self.instance.instancepermission_set.all():
            CatalogIndexPermission.objects.update_or_create(
                catalog_index=catalog_index, team=permission.team
            )


class ExtractStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    REQUESTED = "REQUESTED", _("Requested")
    SUCCESS = "SUCCESS", _("Success")
    FAILED = "FAILED", _("Failed")


class ExtractQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        return self.filter(user=user)


class Extract(Base):
    data_elements = models.ManyToManyField("DataElement")
    indicators = models.ManyToManyField("Indicator")
    period = models.CharField(max_length=200)
    status = models.CharField(max_length=100, choices=ExtractStatus.choices)
    user = models.ForeignKey("user_management.User", on_delete=models.CASCADE)

    objects = ExtractQuerySet.as_manager()

    @property
    def display_name(self):
        return f"{_('Extract')} {date_format(self.created_at)}"
