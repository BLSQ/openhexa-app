from django.contrib import admin
from .models import (
    S3Bucket,
    S3Credentials,
    S3Object,
)


@admin.register(S3Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("username", "user")
    search_fields = ("username",)


@admin.register(S3Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "s3_name", "last_synced_at")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(S3Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("s3_name", "key", "s3_type", "size")
    list_filter = ("s3_type",)
    search_fields = ("s3_name",)
