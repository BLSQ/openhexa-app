from django.contrib import admin

from .models import SupersetDashboard, SupersetInstance


@admin.register(SupersetInstance)
class SupersetInstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created_at", "updated_at")
    search_fields = ("name", "url")
    list_filter = ("created_at", "updated_at")


@admin.register(SupersetDashboard)
class SupersetDashboardAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "external_id",
        "superset_instance",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "external_id")
    list_filter = ("superset_instance", "created_at", "updated_at")
