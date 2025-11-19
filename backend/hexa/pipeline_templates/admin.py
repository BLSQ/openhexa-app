from django.contrib import admin

from hexa.core.admin import GlobalObjectsModelAdmin
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion


@admin.register(PipelineTemplate)
class PipelineTemplateAdmin(GlobalObjectsModelAdmin):
    list_display = ("name", "code", "workspace", "validated_at", "is_deleted")
    list_filter = ("workspace", "validated_at")
    search_fields = ("id", "code", "name")
    fields = (
        "name",
        "code",
        "description",
        "workspace",
        "source_pipeline",
        "functional_type",
        "tags",
        "validated_at",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(PipelineTemplateVersion)
class PipelineTemplateVersionAdmin(admin.ModelAdmin):
    list_display = ("version_number", "template", "created_at")
    list_filter = ("template", "template__workspace")
    search_fields = ("template__name", "template__code", "template__id")
    autocomplete_fields = ["source_pipeline_version"]
