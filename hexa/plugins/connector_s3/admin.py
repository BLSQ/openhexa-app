from django.contrib import admin
from .models import (
    Bucket,
)


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "s3_name", "last_synced_at")
    list_filter = ("name",)
    search_fields = ("name",)
