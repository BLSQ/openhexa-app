from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import Content, Datasource, CatalogIndex
from hexa.common.models import Base
from .api import Dhis2Client
from .sync import sync_from_dhis2_results


class InstanceQuerySet(models.QuerySet):
    def for_user(self, user):
        if not (user.is_active and user.is_superuser):
            return self.none()

        return self


class Instance(Datasource):
    class Meta:
        verbose_name = "DHIS2 Instance"
        ordering = ("name",)

    api_url = models.URLField()
    api_username = models.CharField(max_length=200)
    api_password = models.CharField(max_length=200)

    objects = InstanceQuerySet.as_manager()

    def sync(self):
        """Sync the datasource by querying the DHIS2 API"""

        client = Dhis2Client(
            url=self.api_url, username=self.api_username, password=self.api_password
        )

        # Sync data elements
        with transaction.atomic():
            data_element_results = sync_from_dhis2_results(
                model_class=DataElement,
                instance=self,
                results=client.fetch_data_elements(),
            )

            # Sync indicator types
            indicator_type_results = sync_from_dhis2_results(
                model_class=IndicatorType,
                instance=self,
                results=client.fetch_indicator_types(),
            )

            # Sync indicators
            indicator_results = sync_from_dhis2_results(
                model_class=Indicator,
                instance=self,
                results=client.fetch_indicators(),
            )

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return data_element_results + indicator_type_results + indicator_results

    @property
    def content_summary(self):
        if self.last_synced_at is None:
            return ""

        return _(
            "%(data_element_count)s data elements, %(indicator_count)s indicators"
        ) % {
            "data_element_count": self.dataelement_set.count(),
            "indicator_count": self.indicator_set.count(),
        }

    def index(self):
        CatalogIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.owner,
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            countries=self.countries,
            content_summary=self.content_summary,
            last_synced_at=self.last_synced_at,
            detail_url=reverse("connector_dhis2:datasource_detail", args=(self.pk,)),
        )


class Dhis2Content(Content):
    class Meta:
        abstract = True
        ordering = ["dhis2_name"]

    dhis2_id = models.CharField(max_length=200)
    instance = models.ForeignKey("Instance", null=False, on_delete=models.CASCADE)
    dhis2_name = models.CharField(max_length=200)
    dhis2_short_name = models.CharField(max_length=100, blank=True)
    dhis2_description = models.TextField(blank=True)
    dhis2_external_access = models.BooleanField()
    dhis2_favorite = models.BooleanField()
    dhis2_created = models.DateTimeField()
    dhis2_last_updated = models.DateTimeField()

    @property
    def display_name(self):
        return self.dhis2_short_name if self.dhis2_short_name != "" else self.dhis2_name


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


class DataElement(Dhis2Content):
    class Meta:
        verbose_name = "DHIS2 Data Element"
        ordering = ("dhis2_name",)

    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_domain_type = models.CharField(choices=DomainType.choices, max_length=100)
    dhis2_value_type = models.CharField(choices=ValueType.choices, max_length=100)
    dhis2_aggregation_type = models.CharField(
        choices=AggregationType.choices, max_length=100
    )

    def index(self):
        CatalogIndex.objects.create_or_update(
            indexed_object=self,
            parent_object=self.instance,
            owner=self.instance.owner,
            name=self.dhis2_name,
            short_name=self.dhis2_short_name,
            description=self.dhis2_description,
            countries=self.instance.countries,
            last_synced_at=self.last_synced_at,
            detail_url=reverse(
                "connector_dhis2:data_element_detail",
                args=(self.instance.pk, self.pk),
            ),
        )


class IndicatorType(Dhis2Content):
    dhis2_number = models.BooleanField()
    dhis2_factor = models.IntegerField()


class Indicator(Dhis2Content):
    class Meta:
        verbose_name = "DHIS2 Indicator"
        ordering = ("dhis2_name",)

    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_indicator_type = models.ForeignKey(
        "IndicatorType", null=True, on_delete=models.SET_NULL
    )
    dhis2_annualized = models.BooleanField()

    def index(self):
        CatalogIndex.objects.create_or_update(
            indexed_object=self,
            parent_object=self.instance,
            owner=self.instance.owner,
            name=self.dhis2_name,
            short_name=self.dhis2_short_name,
            description=self.dhis2_description,
            countries=self.instance.countries,
            last_synced_at=self.last_synced_at,
            detail_url=reverse(
                "connector_dhis2:indicator_detail",
                args=(self.instance.pk, self.pk),
            ),
        )
