from django.contrib import admin

from hexa.pipelines.models import PipelineIndex, PipelineIndexPermission


@admin.register(PipelineIndex)
class CatalogIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "content_type")
    list_filter = ("index_type",)
    search_fields = ("name", "short_name")


@admin.register(PipelineIndexPermission)
class CatalogIndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("pipeline_index", "team")
