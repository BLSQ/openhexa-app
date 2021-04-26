from django.contrib import admin

from hexa.pipelines.models import PipelinesIndex, PipelinesIndexPermission


@admin.register(PipelinesIndex)
class CatalogIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "content_type")
    list_filter = ("index_type",)
    search_fields = ("name", "short_name")


@admin.register(PipelinesIndexPermission)
class CatalogIndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("pipeline_index", "team")
