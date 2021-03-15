from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User, Organization
from ..common.admin import country_list

# We won't be using the Django group feature
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "organization_type", country_list)
