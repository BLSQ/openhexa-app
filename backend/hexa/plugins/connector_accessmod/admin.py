from django.contrib import admin
from django.db.models.functions import Collate

from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AccessmodProfile,
    AccessRequest,
    AccessRequestStatus,
    File,
    Fileset,
    FilesetRole,
    Project,
    ProjectPermission,
    ZonalStatisticsAnalysis,
)


class PermissionInline(admin.StackedInline):
    extra = 1
    model = ProjectPermission


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "author", "created_at")
    list_filter = ("author",)
    search_fields = ("name",)

    inlines = [PermissionInline]


@admin.register(FilesetRole)
class FilesetRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "format", "created_at")
    list_filter = ("format",)
    search_fields = ("name",)


@admin.register(Fileset)
class FilesetAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "role", "author", "created_at")
    list_filter = ("status", "role", "project__name", "author")
    search_fields = ("name",)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("uri", "mime_type", "fileset", "created_at")
    list_filter = ("mime_type",)
    search_fields = ("uri",)


@admin.register(AccessibilityAnalysis)
class AccessibilityAnalysisAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "project", "author", "dag_run", "created_at")
    list_filter = ("status", "project__name", "author")
    search_fields = ("name",)


@admin.register(ZonalStatisticsAnalysis)
class ZonalStatisticsAnalysisAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "project", "author", "dag_run", "created_at")
    list_filter = ("status", "project__name", "author")
    search_fields = ("name",)


@admin.register(ProjectPermission)
class ProjectPermissionAdmin(admin.ModelAdmin):
    list_display = ("project", "team", "user", "mode", "created_at")


@admin.action(description="Approve the selected requests")
def approve_requests(modeladmin, request, queryset):
    for access_request in queryset.filter(status=AccessRequestStatus.PENDING):
        access_request.approve_if_has_perm(request.user, request=request)


@admin.action(description="Deny the selected requests")
def deny_requests(modeladmin, request, queryset):
    for access_request in queryset.filter(status=AccessRequestStatus.PENDING):
        access_request.deny_if_has_perm(request.user)


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "accepted_tos",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("first_name", "last_name", "case_insensitive_email")
    actions = [approve_requests, deny_requests]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                case_insensitive_email=Collate("email", "und-x-icu"),
            )
        )


@admin.register(AccessmodProfile)
class AccessmodProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "accepted_tos",
        "is_accessmod_superuser",
        "created_at",
    )
