from django.contrib import admin

from .models import QueryLog, SavedQuery


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("workspace", "user", "status", "origin", "target", "created_at")
    list_select_related = ("workspace", "user")
    list_filter = ("status", "origin", "target", "workspace")
    search_fields = ("workspace__slug", "workspace__name", "user__email", "query")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in QueryLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SavedQuery)
class SavedQueryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "workspace",
        "organization",
        "created_by",
        "visibility",
        "created_at",
        "updated_at",
    )
    list_filter = ("visibility", "workspace__organization")
    list_select_related = ("workspace__organization", "created_by")
    readonly_fields = ("slug",)
    search_fields = (
        "id",
        "name",
        "slug",
        "workspace__name",
        "workspace__slug",
        "workspace__organization__name",
        "created_by__email",
    )
    autocomplete_fields = ("workspace", "created_by")
    fields = (
        "name",
        "slug",
        "description",
        "workspace",
        "created_by",
        "visibility",
        "content",
    )

    @admin.display(ordering="workspace__organization")
    def organization(self, obj):
        return obj.workspace.organization
