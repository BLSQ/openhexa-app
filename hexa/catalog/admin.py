from django.contrib import admin
from hexa.catalog.models import Index, IndexPermission


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = (
        "external_name",
        "app_label",
        "model",
    )
    list_filter = ("content_type__app_label",)
    search_fields = (
        "name",
        "external_name",
    )

    def app_label(self, obj):
        return obj.content_type.app_label

    def model(self, obj):
        return obj.content_type.model


@admin.register(IndexPermission)
class IndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("index", "team")
