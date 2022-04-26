from django.contrib import admin

from .models import (
    ExternalDashboard,
    ExternalDashboardPermission,
    Index,
    IndexPermission,
)


class PermissionInline(admin.TabularInline):
    extra = 1
    model = ExternalDashboardPermission


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "content",
        "app_label",
        "model",
    )
    list_filter = ("content_type",)
    search_fields = ("label", "content")

    def app_label(self, obj):
        return obj.content_type.app_label

    def model(self, obj):
        return obj.content_type.model


@admin.register(IndexPermission)
class IndexPermissionAdmin(admin.ModelAdmin):
    list_display = ("index", "team")


@admin.register(ExternalDashboard)
class ExternalDashboardAdmin(admin.ModelAdmin):
    list_display = ("url",)
    search_fields = ("url",)

    def app_label(self, obj):
        return obj.content_type.app_label

    def model(self, obj):
        return obj.content_type.model


@admin.register(ExternalDashboardPermission)
class ExternalDashboardPermissionAdmin(admin.ModelAdmin):
    list_display = ("external_dashboard", "team", "user", "mode")
