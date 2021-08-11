from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User, Organization, Team, Membership
from hexa.core.admin import country_list

# We won't be using the Django group feature
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "organization_type", country_list)


class MembershipInline(admin.TabularInline):
    model = Membership


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        MembershipInline,
    ]
