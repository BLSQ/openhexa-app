from django.contrib import admin
from hexa.catalog.models import CatalogIndex


@admin.register(CatalogIndex)
class CatalogIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "content_type")
    list_filter = ("index_type",)
    search_fields = ("name", "short_name")
