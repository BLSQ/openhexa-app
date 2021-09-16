from django.contrib import admin

from hexa.pipelines.models import Index, IndexPermission


@admin.register(Index)
class PipelinesIndexAdmin(admin.ModelAdmin):
    # list_display = ("name", "short_name", "content_type")
    # list_filter = ("index_type",)
    # search_fields = ("name", "short_name")
    pass


@admin.register(IndexPermission)
class PipelinesIndexPermissionAdmin(admin.ModelAdmin):
    # list_display = ("pipeline_index", "team")
    pass
