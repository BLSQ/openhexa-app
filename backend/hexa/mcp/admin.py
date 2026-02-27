from django.contrib import admin

from .models import ToolCall


@admin.register(ToolCall)
class ToolCallAdmin(admin.ModelAdmin):
    list_display = ("tool_name", "user", "success", "created_at")
    list_filter = ("success", "tool_name", "created_at")
    search_fields = ("tool_name", "user__email")
    readonly_fields = (
        "user",
        "tool_name",
        "arguments",
        "success",
        "error",
        "created_at",
    )
    ordering = ("-created_at",)
