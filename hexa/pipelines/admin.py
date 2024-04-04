from django.contrib import admin

from hexa.core.admin import GlobalObjectsModelAdmin
from hexa.pipelines.models import Pipeline, PipelineRun, PipelineVersion


@admin.action(description="Restore selected pipelines")
def restore_pipelines(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


@admin.register(Pipeline)
class PipelineAdmin(GlobalObjectsModelAdmin):
    list_display = ("name", "code", "workspace", "deleted_at", "restored_at")
    list_filter = ("workspace",)
    search_fields = ("code", "name")
    actions = [restore_pipelines]


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ("pipeline", "trigger_mode", "state", "execution_date")
    list_filter = ("trigger_mode", "state", "execution_date")


@admin.register(PipelineVersion)
class PipelineVersionAdmin(admin.ModelAdmin):
    list_display = ("pipeline", "number", "created_at")
    list_filter = ("created_at",)
