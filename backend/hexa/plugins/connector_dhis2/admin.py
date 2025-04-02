from django.contrib import admin

from .models import (
    Credentials,
    DataElement,
    DataSet,
    Indicator,
    IndicatorType,
    Instance,
    InstancePermission,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("api_url", "username")
    search_fields = ("api_url", "username")


class PermissionInline(admin.TabularInline):
    extra = 1
    model = InstancePermission


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ("url", "display_name", "slug", "last_synced_at", "auto_sync")
    list_filter = ("url",)
    search_fields = ("url", "name")
    prepopulated_fields = {"slug": ("name",)}

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
        "display_name",
        "dhis2_id",
        "number",
        "factor",
    )
    search_fields = [
        "dhis2_id",
        "name",
        "short_name",
        "short_name",
    ]


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

    search_fields = [
        "dhis2_id",
        "name",
        "short_name",
        "code",
    ]


@admin.register(InstancePermission)
class InstancePermissionAdmin(admin.ModelAdmin):
    list_display = ("instance", "team", "user", "mode", "enable_notebooks_credentials")
