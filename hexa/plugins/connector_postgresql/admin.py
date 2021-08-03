from django.contrib import admin
from .models import PostgresqlDatabase


@admin.register(PostgresqlDatabase)
class PostgresqlDatabaseAdmin(admin.ModelAdmin):
    list_display = ("database", "hostname", "port", "username")
