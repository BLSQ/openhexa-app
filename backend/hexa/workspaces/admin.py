from django.contrib import admin
from django.urls import path

from hexa.workspace_copier.admin import copy_workspace_view

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
    list_display = (
        "slug",
        "name",
        "organization",
        "docker_image",
        "db_name",
        "archived",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "archived",
        "organization",
        ("docker_image", admin.EmptyFieldListFilter),
    )
    readonly_fields = ("created_at", "updated_at", "archived_at")

    search_fields = (
        "slug",
        "name",
        "db_name",
    )

    inlines = [WorkspaceMembershipInline, WorkspaceInvitationInline]
    change_list_template = "admin/workspaces/workspace/change_list.html"

    def get_urls(self):
        custom = [
            path(
                "copy/",
                self.admin_site.admin_view(copy_workspace_view),
                name="workspaces_workspace_copy",
            ),
        ]
        return custom + super().get_urls()


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
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "workspace__name",
        "workspace__slug",
    )
    autocomplete_fields = (
        "workspace",
        "user",
    )


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
