from django.contrib import admin
from .models import (
    ComposerEnvironment,
    Credentials,
    ComposerEnvironmentPermission,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("service_account_email", "oidc_target_audience", "team")
    search_fields = ("service_account_email",)


@admin.register(ComposerEnvironment)
class BucketAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
    )
    search_fields = ("name",)


@admin.register(ComposerEnvironmentPermission)
class ComposerEnvironmentPermissionAdmin(admin.ModelAdmin):
    list_display = ("composer_environment", "team")
