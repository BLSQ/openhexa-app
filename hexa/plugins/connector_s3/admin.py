from django.contrib import admin
from .models import (
    Bucket,
    Credentials,
    Object,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("username",)
    list_filter = ("username",)
    search_fields = ("username",)


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "s3_name", "last_synced_at")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("s3_name", "key", "s3_type", "size")
    list_filter = ("s3_type",)
    search_fields = ("s3_name",)
