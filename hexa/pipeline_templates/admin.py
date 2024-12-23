from django.contrib import admin

from hexa.core.admin import GlobalObjectsModelAdmin
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion


@admin.register(PipelineTemplate)
class PipelineTemplateAdmin(GlobalObjectsModelAdmin):
    list_display = ("name", "code", "workspace")
    list_filter = ("workspace",)
    search_fields = ("id", "code", "name")


@admin.register(PipelineTemplateVersion)
class PipelineTemplateVersionAdmin(admin.ModelAdmin):
    list_display = ("version_number", "template", "created_at")
    list_filter = ("template", "template__workspace")
    search_fields = ("template__name", "template__code", "template__id")
