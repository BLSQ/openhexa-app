from django.contrib import admin

from hexa.plugins.connector_accessmod.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "owner")
    list_filter = ("name",)
    search_fields = ("name",)
