from django.contrib import admin

from .models import (
    Connection,
    ConnectionField,
    Workspace,
    WorkspaceInvitation,
    WorkspaceMembership,
)


class WorkspaceMembershipInline(admin.TabularInline):
    fields = ("user", "role")
    model = WorkspaceMembership
    extra = 0


class WorkspaceInvitationInline(admin.TabularInline):
    model = WorkspaceInvitation
    extra = 0


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "created_at", "updated_at")
    list_filter = ("archived",)

    search_fields = (
        "slug",
        "name",
    )

    inlines = [WorkspaceMembershipInline, WorkspaceInvitationInline]


@admin.register(WorkspaceMembership)
class WorkspaceMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "workspace",
        "user",
        "role",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("notebooks_server_hash",)


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
