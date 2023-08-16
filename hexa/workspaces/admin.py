from django.contrib import admin

from .models import (
    Connection,
    ConnectionField,
    Workspace,
    WorkspaceInvitation,
    WorkspaceMembership,
)


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "created_at", "updated_at", "archived")
    list_filter = ("archived",)
    search_fields = (
        "slug",
        "name",
    )


@admin.register(WorkspaceMembership)
class WorkspaceMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "workspace",
        "user",
        "role",
        "created_at",
        "updated_at",
    )


class ConnectionFieldInline(admin.StackedInline):
    model = ConnectionField


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "workspace",
        "name",
        "connection_type",
        "id",
    )
    inlines = [ConnectionFieldInline]


@admin.register(ConnectionField)
class ConnectionFieldAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "connection",
        "code",
    )


@admin.register(WorkspaceInvitation)
class WorkspaceInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "invited_by",
        "workspace",
        "status",
        "created_at",
        "updated_at",
    )
