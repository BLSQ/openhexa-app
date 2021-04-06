from django.contrib import admin
from .models import (
    Instance,
    DataElement,
    Indicator,
    IndicatorType,
)


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ("hexa_name", "hexa_url", "hexa_last_synced_at")
    list_filter = ("hexa_name",)
    search_fields = ("hexa_name",)


@admin.register(DataElement)
class DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "dhis2_id",
        "name",
        "code",
        "domain_type",
        "value_type",
        "aggregation_type",
    )
    list_filter = ("instance__hexa_name",)
    search_fields = ["name", "short_name", "dhis2_id", "code"]


@admin.register(IndicatorType)
class IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = (
        "dhis2_id",
        "name",
        "number",
        "factor",
    )


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "dhis2_id",
        "name",
        "indicator_type",
    )
    list_filter = ("instance__hexa_name",)
    search_fields = ["name", "short_name", "dhis2_id", "code"]
