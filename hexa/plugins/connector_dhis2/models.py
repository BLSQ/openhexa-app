from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import (
    Content as BaseContent,
    Datasource,
    CatalogIndex,
    CatalogIndexPermission,
)
from hexa.core.models import Base, Permission, RichContent
from .api import Dhis2Client
from .sync import sync_from_dhis2_results
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
        ordering = ("name",)

    api_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )

    objects = InstanceQuerySet.as_manager()

    def sync(self, user):
        """Sync the datasource by querying the DHIS2 API"""

        client = Dhis2Client(
            url=self.api_credentials.api_url,
            username=self.api_credentials.username,
            password=self.api_credentials.password,
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
        catalog_index = CatalogIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.owner,
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            countries=self.countries,
            last_synced_at=self.last_synced_at,
            detail_url=reverse("connector_dhis2:instance_detail", args=(self.pk,)),
            content_summary=self.content_summary,
        )
        for permission in self.instancepermission_set.all():
            CatalogIndexPermission.objects.create(
                catalog_index=catalog_index, team=permission.team
            )


class InstancePermission(Permission):
    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)


class Content(BaseContent):
    class Meta:
        abstract = True
        ordering = ["name"]

    instance = models.ForeignKey("Instance", null=False, on_delete=models.CASCADE)
    dhis2_id = models.CharField(max_length=200)
    dhis2_name = models.TextField()
    dhis2_short_name = models.CharField(max_length=200, blank=True)
    dhis2_description = models.TextField(blank=True)
    dhis2_external_access = models.BooleanField()
    dhis2_favorite = models.BooleanField()
    dhis2_created = models.DateTimeField()
    dhis2_last_updated = models.DateTimeField()

    @property
    def hexa_or_dhis2_short_name(self):
        return self.short_name if self.short_name != "" else self.dhis2_short_name

    @property
    def hexa_or_dhis2_name(self):
        return self.name if self.name != "" else self.dhis2_name

    @property
    def hexa_or_dhis2_description(self):
        return self.description if self.description != "" else self.dhis2_description

    @property
    def display_name(self):
        return (
            self.hexa_or_dhis2_short_name
            if self.hexa_or_dhis2_short_name != ""
            else self.hexa_or_dhis2_name
        )

    @property
    def tags(self):
        return []

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


class DataElement(Content):
    class Meta:
        verbose_name = "DHIS2 Data Element"
        ordering = ("name",)

    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_domain_type = models.CharField(choices=DomainType.choices, max_length=100)
    dhis2_value_type = models.CharField(choices=ValueType.choices, max_length=100)
    dhis2_aggregation_type = models.CharField(
        choices=AggregationType.choices, max_length=100
    )

    def index(self):
        catalog_index = CatalogIndex.objects.create_or_update(
            indexed_object=self,
            parent_object=self.instance,
            owner=self.instance.owner,
            name=self.name,
            external_name=self.dhis2_name,
            short_name=self.short_name,
            external_short_name=self.dhis2_short_name,
            description=self.description,
            external_description=self.dhis2_description,
            countries=self.instance.countries,
            last_synced_at=self.instance.last_synced_at,
            detail_url=reverse(
                "connector_dhis2:data_element_detail",
                args=(self.instance.pk, self.pk),
            ),
        )

        for permission in self.instance.instancepermission_set.all():
            CatalogIndexPermission.objects.create(
                catalog_index=catalog_index, team=permission.team
            )


class IndicatorType(Content):
    class Meta:
        verbose_name = "DHIS2 Indicator type"
        ordering = ("name",)

    dhis2_number = models.BooleanField()
    dhis2_factor = models.IntegerField()


class Indicator(Content):
    class Meta:
        verbose_name = "DHIS2 Indicator"
        ordering = ("name",)

    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_indicator_type = models.ForeignKey(
        "IndicatorType", null=True, on_delete=models.SET_NULL
    )
    dhis2_annualized = models.BooleanField()

    def index(self):
        catalog_index = CatalogIndex.objects.create_or_update(
            indexed_object=self,
            parent_object=self.instance,
            owner=self.instance.owner,
            name=self.name,
            external_name=self.dhis2_name,
            short_name=self.short_name,
            external_short_name=self.dhis2_short_name,
            description=self.description,
            external_description=self.dhis2_description,
            countries=self.instance.countries,
            last_synced_at=self.instance.last_synced_at,
            detail_url=reverse(
                "connector_dhis2:indicator_detail",
                args=(self.instance.pk, self.pk),
            ),
        )

        for permission in self.instance.instancepermission_set.all():
            CatalogIndexPermission.objects.create(
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
