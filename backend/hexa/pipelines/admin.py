from django.contrib import admin

from hexa.core.admin import GlobalObjectsModelAdmin
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
class PipelineAdmin(GlobalObjectsModelAdmin):
    readonly_fields = ("workspace", "source_template", "scheduled_pipeline_version")
    list_display = ("name", "code", "workspace")
    list_select_related = ("workspace",)
    list_filter = ("workspace",)
    search_fields = ("id", "code", "name")
    actions = [restore_pipelines]


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    readonly_fields = ("pipeline", "pipeline_version")
    list_display = (
        "run_id",
        "pipeline",
        "state",
        "execution_date",
        "duration",
        "limits",
    )
    list_select_related = ("pipeline",)
    list_filter = ("trigger_mode", "state", "execution_date")
    search_fields = ("pipeline__name", "pipeline__code", "pipeline__id", "id")
    date_hierarchy = "execution_date"

    @admin.display(description="Limits (CPU / Memory / Timeout)")
    def limits(self, obj):
        return f"{obj.cpu_limit} / {obj.memory_limit} / {obj.timeout}"


@admin.register(PipelineVersion)
class PipelineVersionAdmin(admin.ModelAdmin):
    list_display = ("version_number", "name", "pipeline", "created_at")
    list_select_related = ("pipeline",)
    list_filter = ("pipeline", "pipeline__workspace")
    search_fields = ("name", "pipeline__name", "pipeline__code", "pipeline__id")


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
