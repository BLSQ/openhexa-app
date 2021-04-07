from django.contrib import admin
from .models import (
    Bucket,
    Credentials,
    Object,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("username", "team")
    search_fields = ("username",)


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "name", "hexa_last_synced_at")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "type", "size", "hexa_last_synced_at")
    list_filter = ("type",)
    search_fields = ("name",)
