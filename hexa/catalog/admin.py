from django.contrib import admin
from hexa.catalog.models import CatalogIndex, CatalogIndexPermission


@admin.register(CatalogIndex)
class CatalogIndexAdmin(admin.ModelAdmin):
    list_display = ("name_or_external_name", "content_type")
    list_filter = ("index_type",)
    search_fields = ("name", "external_name", "short_name", "external_short_name")


@admin.register(CatalogIndexPermission)
class CatalogIndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("catalog_index", "team")
