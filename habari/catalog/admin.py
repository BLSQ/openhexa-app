from django.contrib import admin
from habari.catalog.models import CatalogIndex


@admin.register(CatalogIndex)
class Dhis2InstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "index_type", "content_type")
    list_filter = ("index_type",)
    search_fields = ("name", "short_name")
