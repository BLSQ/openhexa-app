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


class PermissionInline(admin.StackedInline):
    extra = 1
    model = BucketPermission


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "last_synced_at")
    list_filter = ("name",)
    search_fields = ("name",)

    inlines = [
        PermissionInline,
    ]


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "key",
        "type",
        "size",
        "orphan",
        "etag",
    )
    list_filter = ("type",)
    search_fields = ("key",)


@admin.register(BucketPermission)
class BucketPermissionAdmin(admin.ModelAdmin):
    list_display = ("bucket", "team")
