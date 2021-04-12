from django.contrib import admin
from hexa.catalog.models import CatalogIndex, CatalogIndexPermission


@admin.register(CatalogIndex)
class CatalogIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "content_type")
    list_filter = ("index_type",)
    search_fields = ("name", "short_name")


@admin.register(CatalogIndexPermission)
class CatalogIndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("catalog_index", "team")
