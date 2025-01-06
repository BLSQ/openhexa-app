from django.contrib import admin

from hexa.connections.models import Connection, ConnectionField


class ConnectionFieldInline(admin.StackedInline):
    model = ConnectionField


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "connection_type",
        "workspace",
        "id",
    )

    list_filter = (
        "workspace",
        "connection_type",
    )

    inlines = [ConnectionFieldInline]


@admin.register(ConnectionField)
class ConnectionFieldAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "connection",
        "code",
    )
