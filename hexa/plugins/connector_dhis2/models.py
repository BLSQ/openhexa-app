from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import Content as BaseContent, Datasource, CatalogIndex
from hexa.common.models import Base
from .api import Dhis2Client
from .sync import sync_from_dhis2_results


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
        ordering = ("hexa_name",)

    url = models.URLField()
    api_url = models.URLField()
    api_username = models.CharField(max_length=200)  # TODO: secure
    api_password = models.CharField(max_length=200)  # TODO: secure

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
            self.hexa_last_synced_at = timezone.now()
            self.save()

        return data_element_results + indicator_type_results + indicator_results

    @property
    def content_summary(self):
        if self.hexa_last_synced_at is None:
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
            owner=self.hexa_owner,
            name=self.hexa_name,
            short_name=self.hexa_short_name,
            description=self.hexa_description,
            countries=self.hexa_countries,
            content_summary=self.content_summary,  # todo: why?
            last_synced_at=self.hexa_last_synced_at,
            detail_url=reverse("connector_dhis2:datasource_detail", args=(self.pk,)),
        )


class InstancePermission(Base):
    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)
    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)


class Content(BaseContent):
    class Meta:
        abstract = True
        ordering = ["name"]

    dhis2_id = models.CharField(max_length=200)
    instance = models.ForeignKey("Instance", null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    external_access = models.BooleanField()
    favorite = models.BooleanField()
    created = models.DateTimeField()
    last_updated = models.DateTimeField()

    @property
    def display_name(self):
        return self.short_name if self.short_name != "" else self.name


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


class DataElement(Content):
    class Meta:
        verbose_name = "DHIS2 Data Element"
        ordering = ("name",)

    code = models.CharField(max_length=100, blank=True)
    domain_type = models.CharField(choices=DomainType.choices, max_length=100)
    value_type = models.CharField(choices=ValueType.choices, max_length=100)
    aggregation_type = models.CharField(choices=AggregationType.choices, max_length=100)

    def index(self):
        CatalogIndex.objects.create_or_update(
            indexed_object=self,
            parent_object=self.instance,
            owner=self.instance.hexa_owner,
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            countries=self.instance.hexa_countries,
            last_synced_at=self.hexa_last_synced_at,
            detail_url=reverse(
                "connector_dhis2:data_element_detail",
                args=(self.instance.pk, self.pk),
            ),
        )


class IndicatorType(Content):
    class Meta:
        verbose_name = "DHIS2 Indicator type"
        ordering = ("name",)

    number = models.BooleanField()
    factor = models.IntegerField()


class Indicator(Content):
    class Meta:
        verbose_name = "DHIS2 Indicator"
        ordering = ("name",)

    code = models.CharField(max_length=100, blank=True)
    indicator_type = models.ForeignKey(
        "IndicatorType", null=True, on_delete=models.SET_NULL
    )
    annualized = models.BooleanField()

    def index(self):
        CatalogIndex.objects.create_or_update(
            indexed_object=self,
            parent_object=self.instance,
            owner=self.instance.hexa_owner,
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            countries=self.instance.hexa_countries,
            last_synced_at=self.hexa_last_synced_at,
            detail_url=reverse(
                "connector_dhis2:indicator_detail",
                args=(self.instance.pk, self.pk),
            ),
        )
