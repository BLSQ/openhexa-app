from django.contrib import admin
from django.urls import path

from hexa.core.admin import GlobalObjectsModelAdmin
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.workspace_copier.admin import copy_templates_view


@admin.register(PipelineTemplate)
class PipelineTemplateAdmin(GlobalObjectsModelAdmin):
    list_display = ("name", "code", "workspace", "validated_at", "is_deleted")
    list_select_related = ("workspace",)
    list_filter = ("validated_at",)
    search_fields = ("id", "code", "name")
    change_list_template = "admin/pipeline_templates/pipelinetemplate/change_list.html"
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
    readonly_fields = ("workspace", "source_pipeline", "created_at", "updated_at")

    def get_urls(self):
        custom = [
            path(
                "copy/",
                self.admin_site.admin_view(copy_templates_view),
                name="pipeline_templates_pipelinetemplate_copy",
            ),
        ]
        return custom + super().get_urls()


@admin.register(PipelineTemplateVersion)
class PipelineTemplateVersionAdmin(admin.ModelAdmin):
    list_display = ("version_number", "template", "created_at")
    list_select_related = ("template",)
    list_filter = ("template__workspace",)
    search_fields = ("template__name", "template__code", "template__id")
    readonly_fields = ("template", "source_pipeline_version")
