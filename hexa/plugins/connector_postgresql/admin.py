from django.contrib import admin
from .models import Database, DatabasePermission, Table


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ("database", "hostname", "port", "username")


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "database")


@admin.register(DatabasePermission)
class DatabasePermissionAdmin(admin.ModelAdmin):
    list_display = ("database", "team")
