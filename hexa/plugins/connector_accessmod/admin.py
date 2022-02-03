from django.contrib import admin

from hexa.plugins.connector_accessmod.models import FilesetRole, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "owner")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(FilesetRole)
class FilesetRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "format")
    list_filter = ("name",)
    search_fields = ("name",)
