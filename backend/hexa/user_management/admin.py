from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.models.functions import Collate
from django.utils.crypto import get_random_string

from hexa.core.admin import country_list

from .models import Feature, FeatureFlag, Membership, Organization, Team, User

# We won't be using the Django group feature
admin.site.unregister(Group)


class UserCreationForm(BaseUserCreationForm):
    """
    A UserCreationForm with optional password inputs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields["password1"].widget.attrs["autocomplete"] = "off"
        self.fields["password2"].widget.attrs["autocomplete"] = "off"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


class FeatureFlagInline(admin.TabularInline):
    model = FeatureFlag
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "last_login",
        "is_staff",
        "is_superuser",
        "teams",
    )

    list_filter = ("last_login", "is_staff", "is_superuser", "is_active")
    inlines = [MembershipInline, FeatureFlagInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password",
                    "analytics_enabled",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_active")}),
    )

    add_form = UserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "description": (
                    "Enter the new user's name and email address and click save."
                    " The user will be emailed a link allowing them to login to"
                    " the site and set their password."
                ),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            "Password",
            {
                "description": "Optionally, you may set the user's password here.",
                "fields": ("password1", "password2"),
                "classes": ("collapse", "collapse-closed"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change and (
            not form.cleaned_data["password1"] or not obj.has_usable_password()
        ):
            # Django's PasswordResetForm won't let us reset an unusable
            # password. We set it above super() so we don't have to save twice.
            obj.set_password(get_random_string(length=10))
            reset_password = True
        else:
            reset_password = False

        super(UserAdmin, self).save_model(request, obj, form, change)
        if reset_password:
            reset_form = PasswordResetForm({"email": obj.email})
            assert reset_form.is_valid()
            reset_form.save(
                request=request,
                use_https=request.is_secure(),
                subject_template_name="user_management/account_creation_subject.txt",
                email_template_name="user_management/account_creation_email.html",
            )

    search_fields = ("case_insensitive_email", "first_name", "last_name")
    ordering = None

    @staticmethod
    def teams(user: User):
        first_teams = list(user.team_set.all()[:2])

        if len(first_teams) == 0:
            return "-"

        team_count = user.team_set.count()
        extra = (
            f" (+{team_count - len(first_teams)})"
            if team_count > len(first_teams)
            else ""
        )

        return f"{', '.join([t.name for t in first_teams])}{extra}"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                case_insensitive_email=Collate("email", "und-x-icu"),
            )
        )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "organization_type", country_list)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "members_count")
    inlines = [
        MembershipInline,
    ]

    def members_count(self, obj):
        return obj.members.count()

    members_count.short_description = "Members Count"


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("code",)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("feature", "user")
    list_filter = ("feature", "user")
