from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import Truncator

from .models import MCPConnection, ToolCall


@admin.register(ToolCall)
class ToolCallAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user_calls",
        "tool_name",
        "workspace",
        "success",
        "short_error",
    )
    list_display_links = ("created_at",)
    list_filter = (
        "success",
        ("user", admin.RelatedOnlyFieldListFilter),
        "tool_name",
    )
    list_select_related = ("user",)
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "tool_name",
        "arguments",
        "error",
    )
    date_hierarchy = "created_at"
    # The exact total needs a second count over the whole table on every search.
    show_full_result_count = False
    readonly_fields = (
        "user",
        "tool_name",
        "arguments",
        "success",
        "error",
        "created_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="User", ordering="user__email")
    def user_calls(self, obj):
        """The user's email, linking to the list narrowed to their calls."""
        url = reverse("admin:mcp_toolcall_changelist")
        return format_html(
            '<a href="{}?user__id__exact={}">{}</a>', url, obj.user_id, obj.user.email
        )

    @admin.display(description="Workspace")
    def workspace(self, obj):
        # Workspace tools name their target `slug`, every other tool `workspace_slug`.
        return obj.arguments.get("workspace_slug") or obj.arguments.get("slug") or "-"

    @admin.display(description="Error")
    def short_error(self, obj):
        return Truncator(obj.error).chars(80)


@admin.register(MCPConnection)
class MCPConnectionAdmin(admin.ModelAdmin):
    list_display = ("user", "application", "last_used_at", "created_at")
    list_select_related = ("user", "application")
    search_fields = ("user__email", "application__name")
    filter_horizontal = ("workspaces", "organizations")
    readonly_fields = ("user", "application", "last_used_at")
