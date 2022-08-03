from django.contrib import admin

from .models import IASOAccount, IASOApiToken, IASOForm, IASOOrgUnit, IASOPermission


@admin.register(IASOAccount)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "api_url", "username")
    search_fields = ("name", "api_url", "username")


@admin.register(IASOPermission)
class IASOAccountPermissionAdmin(admin.ModelAdmin):
    list_display = ("iaso_account", "team", "user", "mode")


@admin.register(IASOForm)
class FormAdmin(admin.ModelAdmin):
    list_display = ("name", "updated")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(IASOOrgUnit)
class OrganisationUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "updated")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(IASOApiToken)
class IASOApiToken(admin.ModelAdmin):
    list_display = ("iaso_account", "user")
    search_fields = ("iaso_account", "user.login")
