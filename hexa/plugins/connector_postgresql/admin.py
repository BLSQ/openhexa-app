from django.contrib import admin
from .models import Database, DatabasePermission


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ("database", "hostname", "port", "username")


@admin.register(DatabasePermission)
class DatabasePermissionAdmin(admin.ModelAdmin):
    list_display = ("database", "team")
