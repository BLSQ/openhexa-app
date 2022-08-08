from django.contrib import admin

from .models import Account, ApiToken, Form, IASOPermission, OrgUnit


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "api_url", "username")
    search_fields = ("name", "api_url", "username")


@admin.register(IASOPermission)
class AccountPermissionAdmin(admin.ModelAdmin):
    list_display = ("iaso_account", "team", "user", "mode")


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("name", "updated")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(OrgUnit)
class OrganisationUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "updated")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(ApiToken)
class ApiToken(admin.ModelAdmin):
    list_display = ("iaso_account", "user")
    search_fields = ("iaso_account", "user.login")
