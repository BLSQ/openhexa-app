from django.contrib import admin

from hexa.workspaces.models import Workspace, WorkspaceDBConfig


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )


@admin.register(WorkspaceDBConfig)
class WorkspaceDBConfigAdmin(admin.ModelAdmin):
    list_display = (
        "hostname",
        "username",
    )

    def has_delete_permission(self, request, obj=None):
        return False
