from django.contrib import admin

from .models import FileAccessRule


@admin.register(FileAccessRule)
class FileAccessRuleAdmin(admin.ModelAdmin):
    list_display = (
        "workspace",
        "path",
        "auth_type",
        "created_at",
        "created_by",
        "expires_at",
    )
    list_filter = ("workspace", "auth_type", "created_by")
    search_fields = ("workspace__name", "path")
