from django.contrib import admin

from .models import *


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ("code", "value")
    ordering = ("code",)
    fields = (
        "id",
        "code",
        "value",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("id", "created_at", "updated_at")
