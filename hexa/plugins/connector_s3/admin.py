from django.contrib import admin

from .models import Bucket, BucketPermission, Credentials, Object


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("username", "app_role_arn")
    search_fields = ("username",)


class PermissionInline(admin.StackedInline):
    extra = 1
    model = BucketPermission


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "last_synced_at", "auto_sync")
    list_filter = ("name",)
    search_fields = ("name",)

    inlines = [
        PermissionInline,
    ]


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "bucket",
        "key",
        "type",
        "size",
        "orphan",
        "etag",
    )
    list_filter = ("type", "bucket")
    search_fields = ("key", "bucket")


@admin.register(BucketPermission)
class BucketPermissionAdmin(admin.ModelAdmin):
    list_display = ("bucket", "team", "mode")
