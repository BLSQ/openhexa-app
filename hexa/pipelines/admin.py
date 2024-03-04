from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from hexa.pipelines.models import (
    Index,
    IndexPermission,
    Pipeline,
    PipelineRun,
    PipelineVersion,
)


@admin.action(description="Restore selected pipelines")
def restore_pipelines(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "workspace", "deleted_at", "restored_at")
    list_filter = ("workspace",)
    search_fields = ("code", "name")
    actions = [restore_pipelines]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Pipeline.all_objects.all()


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ("pipeline", "trigger_mode", "state", "execution_date")
    list_filter = ("trigger_mode", "state", "execution_date")


@admin.register(PipelineVersion)
class PipelineVersionAdmin(admin.ModelAdmin):
    list_display = ("pipeline", "number", "created_at")
    list_filter = ("created_at",)


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
