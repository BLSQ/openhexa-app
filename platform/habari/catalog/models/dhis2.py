from dhis2 import Api
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import Base, Content
from .common import SourceType


class Dhis2Connection(Base):
    source = models.OneToOneField(
        "Datasource", on_delete=models.CASCADE, related_name="connection"
    )
    api_url = models.URLField()
    api_username = models.CharField(max_length=200)
    api_password = models.CharField(max_length=200)

    def refresh(self):
        dhis2 = Api("play.dhis2.org/demo", "admin", "district")
        de_results = dhis2.get_paged(
            "dataElements", params={"fields": ":all"}, page_size=100, merge=True
        )
        de_list = de_results["dataElements"]
        for de in de_list:
            try:
                description = next(
                    p
                    for p in de["translations"]
                    if p["property"] == "DESCRIPTION" and "en_" in p["locale"]
                )["value"]
            except StopIteration:
                try:
                    description = next(
                        p for p in de["translations"] if p["property"] == "DESCRIPTION"
                    )["value"]
                except StopIteration:
                    description = ""

            Dhis2DataElement.objects.create(
                source=self.source,
                dhis2_id=de["id"],
                dhis2_code=de.get("code", ""),
                name=de["name"],
                short_name=de["shortName"],
                description=description,
                dhis2_domain_type=de["domainType"],
                dhis2_value_type=de["valueType"],
                dhis2_aggregation_type=de["aggregationType"],
            )

        return f"Synced {len(de_list)} data elements"


class Dhis2Area(Content):
    pass


class Dhis2Theme(Content):
    pass


class Dhis2Data(Content):
    class Meta:
        abstract = True

    owner = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    source = models.ForeignKey(
        "Datasource",
        on_delete=models.CASCADE,
        limit_choices_to={"source_type": SourceType.DHIS2.value},
    )
    area = models.ForeignKey(
        "Dhis2Area", null=True, blank=True, on_delete=models.SET_NULL
    )
    theme = models.ForeignKey(
        "Dhis2Theme", null=True, blank=True, on_delete=models.SET_NULL
    )
    dhis2_id = models.CharField(max_length=100)
    dhis2_code = models.CharField(max_length=100, blank=True)


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
    POSITIVE_INTEGER = "POSITIVE_INTEGER", _("Positive Integer")
    NEGATIVE_INTEGER = "NEGATIVE_INTEGER", _("Negative Integer")
    POSITIVE_OR_ZERO_INTEGER = "POSITIVE_OR_ZERO_INTEGER", _("Positive or Zero Integer")
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


class Dhis2DataElement(Dhis2Data):
    dhis2_domain_type = models.CharField(
        choices=Dhis2DomainType.choices, max_length=100
    )
    dhis2_value_type = models.CharField(choices=Dhis2ValueType.choices, max_length=100)
    dhis2_aggregation_type = models.CharField(
        choices=Dhis2AggregationType.choices, max_length=100
    )


class Dhis2IndicatorType(models.TextChoices):
    NUMBER_FACTOR_1 = "NUMBER_FACTOR_1", _("Number (Factor 1)")
    PER_CENT = "PER_CENT", _("Per cent")
    PER_HUNDRED_THOUSANDS = "PER_HUNDRED_THOUSANDS", _("Per hundred thousand")
    PER_TEN_THOUSAND = "PER_TEN_THOUSAND", _("Per ten thousand")
    PER_THOUSAND = "PER_THOUSAND", _("Per thousand")


class Dhis2Indicator(Dhis2Data):
    dhis2_indicator_type = models.CharField(
        choices=Dhis2IndicatorType.choices, max_length=100
    )
    annualized = models.BooleanField()
