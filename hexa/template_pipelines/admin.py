from django.contrib import admin

from hexa.core.admin import GlobalObjectsModelAdmin
from hexa.template_pipelines.models import Template, TemplateVersion


@admin.register(Template)
class TemplateAdmin(GlobalObjectsModelAdmin):
    list_display = ("name", "code", "workspace")
    list_filter = ("workspace",)
    search_fields = ("id", "code", "name")


@admin.register(TemplateVersion)
class PipelineVersionAdmin(admin.ModelAdmin):
    list_display = ("version_number", "template", "created_at")
    list_filter = ("template", "template__workspace")
    search_fields = ("template__name", "template__code", "template__id")
