from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from habari.catalog.connectors import ContentSummary, SyncResult
from habari.catalog.models import ExternalContent, Connector
from habari.common.models import Base
from .api import Dhis2Client


class Dhis2Connector(Connector):
    api_url = models.URLField()
    api_username = models.CharField(max_length=200)
    api_password = models.CharField(max_length=200)

    def sync(self):
        """Sync the datasource by querying the DHIS2 API"""

        client = Dhis2Client(
            url=self.api_url, username=self.api_username, password=self.api_password
        )

        # Sync DE
        de_result = Dhis2DataElement.objects.sync_from_dhis2_results(
            self.datasource, client.fetch_data_elements()
        )

        # Sync DI
        di_result = Dhis2Indicator.objects.sync_from_dhis2_results(
            self.datasource, client.fetch_indicators()
        )

        return de_result + di_result

    def get_content_summary(self):
        return ContentSummary(
            data_elements=self.datasource.dhis2dataelement_set.count(),
            data_indicators=self.datasource.dhis2indicator_set.count(),
        )


class Dhis2Data(ExternalContent):
    class Meta:
        abstract = True
        ordering = ["dhis2_name"]

    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_name = models.CharField(max_length=200)
    dhis2_short_name = models.CharField(max_length=100, blank=True)
    dhis2_description = models.TextField(blank=True)

    @property
    def display_name(self):
        return self.dhis2_short_name if self.dhis2_short_name != "" else self.dhis2_name


class Dhis2DomainType(models.TextChoices):
    AGGREGATE = "AGGREGATE", _("Aggregate")
    TRACKER = "TRACKER", _("Tracker")


class Dhis2ValueType(models.TextChoices):
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
    # TODO: check order of the next 6 items
    POSITIVE_INTEGER = "POSITIVE_INTEGER", _("Positive Integer")
    INTEGER_POSITIVE = "INTEGER_POSITIVE", _("Positive Integer")
    NEGATIVE_INTEGER = "NEGATIVE_INTEGER", _("Negative Integer")
    INTEGER_NEGATIVE = "INTEGER_NEGATIVE", _("Negative Integer")
    POSITIVE_OR_ZERO_INTEGER = "POSITIVE_OR_ZERO_INTEGER", _("Positive or Zero Integer")
    INTEGER_ZERO_OR_POSITIVE = "INTEGER_ZERO_OR_POSITIVE", _("Positive or Zero Integer")
    TRACKER_ASSOCIATE = "TRACKER_ASSOCIATE", _("Tracker Associate")
    USERNAME = "USERNAME", _("Username")
    COORDINATE = "COORDINATE", _("Coordinate")
    ORGANISATION_UNIT = "ORGANISATION_UNIT", _("Organisation Unit")
    AGE = "AGE", _("Age")
    URL = "URL", _("URL")
    FILE = "FILE", _("File")
    IMAGE = "IMAGE", _("Image")


class Dhis2AggregationType(models.TextChoices):
    SUM = "SUM", _("Sum")
    AVERAGE = "AVERAGE", _("Average")
    # TODO: complete


class Dhis2QuerySet(models.QuerySet):
    FIELD_MAPPINGS = {}

    def sync_from_dhis2_results(self, datasource, items):
        """Iterate over the DEs in the response and create, update or ignore depending on local data"""

        created = 0
        updated = 0
        identical = 0

        for item in items:
            field_values = {
                field_name: item[dhis2_key]
                for field_name, dhis2_key in self.FIELD_MAPPINGS.items()
            }

            try:
                # Check if the DE is already in our database and compare values (local vs dhis2)
                existing_de = self.get(external_id=item["id"])
                existing_field_values = {
                    field_name: getattr(existing_de, field_name)
                    for field_name, dhis2_key in self.FIELD_MAPPINGS.items()
                }
                diff_field_values = {
                    field_name: field_values[field_name]
                    for field_name in self.FIELD_MAPPINGS.keys()
                    if field_values[field_name] != existing_field_values[field_name]
                }

                # Check if we need to actually update the local version
                if len(diff_field_values) > 0:
                    for field_name in diff_field_values:
                        setattr(existing_de, field_name, diff_field_values[field_name])
                    updated += 1
                else:
                    identical += 1
            # If we don't have the DE locally, create it
            except ObjectDoesNotExist:
                super().create(**field_values, datasource=datasource)
                created += 1

        return SyncResult(
            datasource=datasource, created=created, updated=updated, identical=identical
        )


class Dhis2DataElementQuerySet(Dhis2QuerySet):
    FIELD_MAPPINGS = {
        "external_id": "id",
        "dhis2_code": "code",
        "dhis2_name": "name",
        "dhis2_short_name": "shortName",
        "dhis2_domain_type": "domainType",
        "dhis2_value_type": "valueType",
        "dhis2_aggregation_type": "aggregationType",
    }


class Dhis2DataElement(Dhis2Data):
    dhis2_domain_type = models.CharField(
        choices=Dhis2DomainType.choices, max_length=100
    )
    dhis2_value_type = models.CharField(choices=Dhis2ValueType.choices, max_length=100)
    dhis2_aggregation_type = models.CharField(
        choices=Dhis2AggregationType.choices, max_length=100
    )

    objects = Dhis2DataElementQuerySet.as_manager()

    @property
    def dhis2_domain_type_label(self):
        try:
            return Dhis2DomainType[self.dhis2_domain_type].label
        except KeyError:
            return "Unknown"

    @property
    def dhis2_value_type_label(self):
        try:
            return Dhis2ValueType[self.dhis2_value_type].label
        except KeyError:
            return "Unknown"

    @property
    def dhis2_aggregation_type_label(self):
        try:
            return Dhis2AggregationType[self.dhis2_aggregation_type].label
        except KeyError:
            return "Unknown"


class Dhis2IndicatorType(models.TextChoices):
    NUMBER_FACTOR_1 = "NUMBER_FACTOR_1", _("Number (Factor 1)")
    PER_CENT = "PER_CENT", _("Per cent")
    PER_HUNDRED_THOUSANDS = "PER_HUNDRED_THOUSANDS", _("Per hundred thousand")
    PER_TEN_THOUSAND = "PER_TEN_THOUSAND", _("Per ten thousand")
    PER_THOUSAND = "PER_THOUSAND", _("Per thousand")


class Dhis2IndicatorQuerySet(Dhis2QuerySet):
    FIELD_MAPPINGS = {
        "external_id": "id",
        "dhis2_code": "code",
        "dhis2_name": "name",
        "dhis2_short_name": "shortName",
        "dhis2_annualized": "annualized",
        # TODO: check
        # "dhis2_indicator_type": "indicatorType",
    }


class Dhis2Indicator(Dhis2Data):
    dhis2_indicator_type = models.CharField(
        choices=Dhis2IndicatorType.choices, max_length=100
    )
    dhis2_annualized = models.BooleanField()

    objects = Dhis2IndicatorQuerySet.as_manager()

    @property
    def dhis2_indicator_type_label(self):
        try:
            return Dhis2IndicatorType[self.dhis2_indicator_type].label
        except KeyError:
            return "Unknown"
