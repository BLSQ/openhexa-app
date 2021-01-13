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

    def __str__(self):
        return f"{type(self).__name__}: {self.id}"


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
        return f"{type(self).__name__}: {self.short_name if self.short_name else self.name}"


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


class SourceType(models.TextChoices):
    DHIS2 = "DHIS2", _("DHIS2")
    IASO = "IASO", _("Iaso")
    FILES = "FILES", _("Files")


class DataSource(Content):
    owner = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    source_type = models.CharField(choices=SourceType.choices, max_length=100)
    url = models.URLField(blank=True)
    active_from = models.DateTimeField(null=True, blank=True)
    active_to = models.DateTimeField(null=True, blank=True)


class Dhis2Data(Content):
    class Meta:
        abstract = True

    owner = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    source = models.ForeignKey(
        "DataSource",
        on_delete=models.CASCADE,
        limit_choices_to={"source_type": SourceType.DHIS2.value},
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
