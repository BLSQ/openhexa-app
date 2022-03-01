from django.contrib import admin

from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    File,
    Fileset,
    FilesetRole,
    Project,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "owner")
    list_filter = ("owner",)
    search_fields = ("name",)


@admin.register(FilesetRole)
class FilesetRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "format")
    list_filter = ("format",)
    search_fields = ("name",)


@admin.register(Fileset)
class FilesetAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "role", "owner")
    list_filter = ("role", "project__name", "owner")
    search_fields = ("name",)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("uri", "mime_type", "fileset")
    list_filter = ("mime_type",)
    search_fields = ("uri",)


@admin.register(AccessibilityAnalysis)
class AccessibilityAnalysisAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "project", "owner", "dag_run")
    list_filter = ("status", "project__name", "owner")
    search_fields = ("name",)
