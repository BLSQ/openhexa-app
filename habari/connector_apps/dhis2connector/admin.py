from django.contrib import admin
from .models import (
    Dhis2Connector,
    Dhis2DataElement,
    Dhis2Indicator,
    Dhis2IndicatorType,
)


def country_list(obj):
    return ",".join(country.alpha3 for country in obj.countries)


country_list.short_description = "Countries"


@admin.register(Dhis2Connector)
class Dhis2ConnectorAdmin(admin.ModelAdmin):
    list_display = ("datasource", "api_url")
    list_filter = ("datasource__name",)
    search_fields = ["datasource__name"]


@admin.register(Dhis2DataElement)
class Dhis2DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "datasource",
        "external_id",
        "dhis2_code",
        "dhis2_domain_type",
        "dhis2_value_type",
        "dhis2_aggregation_type",
    )
    list_filter = ("datasource__name",)
    search_fields = ["dhis2_name", "dhis2_short_name", "external_id", "dhis2_code"]


@admin.register(Dhis2IndicatorType)
class Dhis2IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "external_id",
        "dhis2_number",
        "dhis2_factor",
    )


@admin.register(Dhis2Indicator)
class Dhis2IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "datasource",
        "external_id",
        "dhis2_indicator_type",
    )
    list_filter = ("datasource__name",)
    search_fields = ["dhis2_name", "dhis2_short_name", "external_id", "dhis2_code"]
