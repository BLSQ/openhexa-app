from django.contrib import admin

from hexa.shortcuts.models import Shortcut


@admin.register(Shortcut)
class ShortcutAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "workspace",
        "content_type",
        "object_id",
        "order",
        "created_at",
    )
    list_filter = ("content_type", "workspace", "created_at")
    search_fields = ("user__email", "workspace__slug", "object_id")
    ordering = ("user", "workspace", "order", "-created_at")
