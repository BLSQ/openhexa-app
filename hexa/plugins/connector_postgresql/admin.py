from django.contrib import admin
from .models import PostgresqlDatabase, PostgresqlDatabasePermission


@admin.register(PostgresqlDatabase)
class PostgresqlDatabaseAdmin(admin.ModelAdmin):
    list_display = ("database", "hostname", "port", "username")


@admin.register(PostgresqlDatabasePermission)
class PostgresqlDatabasePermissionAdmin(admin.ModelAdmin):
    list_display = ("database", "team")
