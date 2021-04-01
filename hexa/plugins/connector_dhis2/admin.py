from django.contrib import admin
from .models import (
    Instance,
    DataElement,
    Indicator,
    IndicatorType,
)


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "last_synced_at")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(DataElement)
class DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "dhis2_id",
        "dhis2_name",
        "dhis2_code",
        "dhis2_domain_type",
        "dhis2_value_type",
        "dhis2_aggregation_type",
    )
    list_filter = ("instance__name",)
    search_fields = ["dhis2_name", "dhis2_short_name", "dhis2_id", "dhis2_code"]


@admin.register(IndicatorType)
class IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = (
        "dhis2_id",
        "dhis2_name",
        "dhis2_number",
        "dhis2_factor",
    )


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "dhis2_id",
        "dhis2_name",
        "dhis2_indicator_type",
    )
    list_filter = ("instance__name",)
    search_fields = ["dhis2_name", "dhis2_short_name", "dhis2_id", "dhis2_code"]
