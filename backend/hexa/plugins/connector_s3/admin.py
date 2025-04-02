from django.contrib import admin

from .models import Bucket, BucketPermission, Object


class PermissionInline(admin.TabularInline):
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
        "etag",
    )
    list_filter = ("type", "bucket")
    search_fields = ("key", "bucket")


@admin.register(BucketPermission)
class BucketPermissionAdmin(admin.ModelAdmin):
    list_display = ("bucket", "team", "user", "mode")
