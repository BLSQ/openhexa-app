from django.contrib import admin

from .models import IASOAccount, IASOForm, IASOPermission


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
