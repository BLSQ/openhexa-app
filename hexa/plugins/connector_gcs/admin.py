from django.contrib import admin

from .models import Bucket, Credentials, GCSBucketPermission, Object


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("service_account", "project_id")
    search_fields = ("service_account",)


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "last_synced_at", "auto_sync")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "bucket",
        "key",
        "type",
        "size",
        "etag",
    )
    list_filter = ("type", "bucket")
    search_fields = ("key", "bucket")


@admin.register(GCSBucketPermission)
class BucketPermissionAdmin(admin.ModelAdmin):
    list_display = ("bucket", "team", "user", "mode")
