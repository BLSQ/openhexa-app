from django.contrib import admin

from hexa.pipelines.models import (
    Index,
    IndexPermission,
    Pipeline,
    PipelineCode,
    PipelineRun,
)


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ("run_id", "state", "execution_date", "pipeline")
    list_filter = ("state", "execution_date", "pipeline")


@admin.register(PipelineCode)
class PipelineCodeAdmin(admin.ModelAdmin):
    list_display = ("display_name",)


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = (
        "external_name",
        "app_label",
        "model",
    )
    list_filter = ("content_type",)
    search_fields = ("external_name",)

    def app_label(self, obj):
        return obj.content_type.app_label

    def model(self, obj):
        return obj.content_type.model


@admin.register(IndexPermission)
class IndexPermissionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    list_display = ("index", "team")
    readonly_fields = (
        "team",
        "permission_type",
        "permission_id",
        "index",
    )
