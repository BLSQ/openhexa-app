from django.contrib import admin
from .models import (
    Bucket,
    Credentials,
    Object,
    BucketPermission,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("username", "use_sts_credentials")
    search_fields = ("username",)


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("s3_name", "name", "last_synced_at")
    list_filter = ("s3_name", "name")
    search_fields = ("s3_name", "name")


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("display_name", "s3_key", "s3_type", "s3_size")
    list_filter = ("s3_type",)
    search_fields = ("name", "s3_name")


@admin.register(BucketPermission)
class BucketPermissionAdmin(admin.ModelAdmin):
    list_display = ("bucket", "team")
