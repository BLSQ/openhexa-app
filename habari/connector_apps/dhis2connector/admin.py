from django.contrib import admin
from .models import (
    Dhis2Instance,
    Dhis2DataElement,
    Dhis2Indicator,
    Dhis2IndicatorType,
)


def country_list(obj):
    return ",".join(country.alpha3 for country in obj.countries)


country_list.short_description = "Countries"


@admin.register(Dhis2Instance)
class Dhis2InstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Dhis2DataElement)
class Dhis2DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "dhis2_instance",
        "dhis2_id",
        "dhis2_code",
        "dhis2_domain_type",
        "dhis2_value_type",
        "dhis2_aggregation_type",
    )
    list_filter = ("dhis2_instance__name",)
    search_fields = ["dhis2_name", "dhis2_short_name", "dhis2_id", "dhis2_code"]


@admin.register(Dhis2IndicatorType)
class Dhis2IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "dhis2_id",
        "dhis2_number",
        "dhis2_factor",
    )


@admin.register(Dhis2Indicator)
class Dhis2IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "dhis2_instance",
        "dhis2_id",
        "dhis2_indicator_type",
    )
    list_filter = ("dhis2_instance__name",)
    search_fields = ["dhis2_name", "dhis2_short_name", "dhis2_id", "dhis2_code"]
