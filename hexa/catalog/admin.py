from django.contrib import admin
from hexa.catalog.models import Index, IndexPermission


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ("name_or_external_name", "content_type")
    list_filter = ("index_type",)
    search_fields = ("name", "external_name", "short_name", "external_short_name")


@admin.register(IndexPermission)
class IndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("index", "team")
