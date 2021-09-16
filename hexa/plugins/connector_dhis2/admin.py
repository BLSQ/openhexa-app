from django.contrib import admin
from .models import (
    Instance,
    DataElement,
    Indicator,
    IndicatorType,
    InstancePermission,
    Credentials,
    DataSet,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("api_url",)
    search_fields = ("api_url",)


class PermissionInline(admin.StackedInline):
    extra = 1
    model = InstancePermission


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ("url", "last_synced_at")
    list_filter = ("url",)
    search_fields = ("url",)

    inlines = [
        PermissionInline,
    ]


@admin.register(DataElement)
class DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "instance",
        "dhis2_id",
        "code",
        "domain_type",
        "value_type",
        "aggregation_type",
    )
    list_filter = ("instance__url",)
    search_fields = [
        "dhis2_id",
        "name",
        "short_name",
        "code",
    ]


@admin.register(IndicatorType)
class IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = (
        "dhis2_id",
        "number",
        "factor",
    )


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "instance",
        "dhis2_id",
        "indicator_type",
    )
    list_filter = ("instance__url",)
    search_fields = [
        "dhis2_id",
        "name",
        "short_name",
        "short_name",
        "code",
    ]


@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "instance",
        "dhis2_id",
    )


@admin.register(InstancePermission)
class InstancePermissionAdmin(admin.ModelAdmin):
    list_display = ("instance", "team")
