from django.contrib import admin
from hexa.catalog.models import Index, IndexPermission


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ("content_type",)
    search_fields = (
        "name",
        "external_name",
    )


@admin.register(IndexPermission)
class IndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("index", "team")
