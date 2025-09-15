from django.contrib import admin

from .models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "created_at", "created_by")
    list_filter = ("workspace", "created_by")
    search_fields = ("id", "name", "workspace__name")


@admin.register(DatasetVersion)
class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ("name", "dataset", "created_at", "created_by")
    list_filter = ("dataset", "created_by")
    search_fields = ("id", "name", "dataset__id", "dataset__name", "workspace__name")


@admin.register(DatasetVersionFile)
class DatasetVersionFileAdmin(admin.ModelAdmin):
    list_display = (
        "filename",
        "dataset_version",
    )
    list_filter = ("dataset_version__dataset", "created_by")
    search_fields = (
        "id",
        "uri",
        "dataset_version__id",
    )


@admin.register(DatasetLink)
class DatasetLinkAdmin(admin.ModelAdmin):
    list_display = ("dataset", "workspace", "created_at", "created_by")
    list_filter = ("dataset", "workspace", "dataset__workspace")
    search_fields = ("dataset__id", "dataset__name", "workspace__name")
