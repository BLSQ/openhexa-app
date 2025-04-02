from django.contrib import admin

from .models import Database, DatabasePermission, Table


class PermissionInline(admin.StackedInline):
    extra = 1
    model = DatabasePermission


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = (
        "database",
        "hostname",
        "port",
        "username",
        "last_synced_at",
        "auto_sync",
    )

    inlines = [
        PermissionInline,
    ]


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "database", "rows")
    search_fields = ("name", "database")
    list_filter = ("database",)


@admin.register(DatabasePermission)
class DatabasePermissionAdmin(admin.ModelAdmin):
    list_display = ("database", "team", "user", "mode")
