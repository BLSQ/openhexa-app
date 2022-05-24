from django.contrib import admin

from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    File,
    Fileset,
    FilesetRole,
    Project,
    ProjectPermission,
)


class PermissionInline(admin.StackedInline):
    extra = 1
    model = ProjectPermission


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "author")
    list_filter = ("author",)
    search_fields = ("name",)

    inlines = [PermissionInline]


@admin.register(FilesetRole)
class FilesetRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "format")
    list_filter = ("format",)
    search_fields = ("name",)


@admin.register(Fileset)
class FilesetAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "role", "author")
    list_filter = ("status", "role", "project__name", "author")
    search_fields = ("name",)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("uri", "mime_type", "fileset")
    list_filter = ("mime_type",)
    search_fields = ("uri",)


@admin.register(AccessibilityAnalysis)
class AccessibilityAnalysisAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "project", "author", "dag_run")
    list_filter = ("status", "project__name", "author")
    search_fields = ("name",)


@admin.register(ProjectPermission)
class ProjectPermissionAdmin(admin.ModelAdmin):
    list_display = ("project", "team", "user", "mode")
