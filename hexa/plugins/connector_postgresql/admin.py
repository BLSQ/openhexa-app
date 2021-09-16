from django.contrib import admin
from .models import Database, DatabasePermission, Table


class PermissionInline(admin.StackedInline):
    extra = 1
    model = DatabasePermission


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ("database", "hostname", "port", "username")

    inlines = [
        PermissionInline,
    ]


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "database")


@admin.register(DatabasePermission)
class DatabasePermissionAdmin(admin.ModelAdmin):
    list_display = ("database", "team")
