from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db.models.functions import Collate
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

from hexa.core.admin import GlobalObjectsModelAdmin, country_list

from .models import (
    Feature,
    FeatureFlag,
    Membership,
    Organization,
    OrganizationInvitation,
    OrganizationMembership,
    OrganizationSubscription,
    ServiceAccount,
    SignupRequest,
    Team,
    User,
)

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
    filter_horizontal = ("user_permissions",)
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
        (
            "Advanced permissions",
            {
                "classes": ("collapse",),
                "fields": ("user_permissions",),
            },
        ),
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


class OrganizationMembershipInline(admin.TabularInline):
    fields = ("user", "role")
    autocomplete_fields = ("user",)
    model = OrganizationMembership
    extra = 0


class OrganizationSubscriptionInline(admin.TabularInline):
    model = OrganizationSubscription
    extra = 0
    fields = (
        "subscription_id",
        "plan_code",
        "start_date",
        "end_date",
        "users_limit",
        "workspaces_limit",
        "pipeline_runs_limit",
    )


@admin.action(description="Restore selected organizations")
def restore_organizations(_modeladmin, _request, queryset):
    for obj in queryset:
        obj.restore()


@admin.register(Organization)
class OrganizationAdmin(GlobalObjectsModelAdmin):
    list_display = (
        "name",
        "short_name",
        "organization_type",
        "workspace_count",
        "is_active",
        "created_at",
        "updated_at",
        country_list,
    )
    search_fields = ("name", "short_name")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    ordering = ("-created_at",)
    inlines = [OrganizationMembershipInline, OrganizationSubscriptionInline]
    actions = [restore_organizations]

    def is_active(self, obj):
        return obj.deleted_at is None

    is_active.boolean = True
    is_active.short_description = "Active"

    def workspace_count(self, obj):
        return obj.workspaces.filter(archived=False).count()

    workspace_count.short_description = "Number of Active Workspaces"

    def response_change(self, request, obj):
        if "_restore" in request.POST:
            obj.restore()
            self.message_user(request, f"Organization '{obj.name}' has been restored.")
        return super().response_change(request, obj)


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


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    list_display = (
        "organization",
        "user",
        "role",
        "created_at",
        "updated_at",
    )


class OrganizationWorkspaceInvitationInline(admin.TabularInline):
    from hexa.workspaces.models import OrganizationWorkspaceInvitation

    model = OrganizationWorkspaceInvitation
    extra = 0
    fields = ("workspace", "role")


@admin.register(OrganizationInvitation)
class OrganizationInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "invited_by",
        "organization",
        "status",
        "created_at",
        "updated_at",
        "role",
    )
    inlines = [OrganizationWorkspaceInvitationInline]


@admin.register(OrganizationSubscription)
class OrganizationSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "plan_code",
        "start_date",
        "end_date",
        "users_limit",
        "workspaces_limit",
        "pipeline_runs_limit",
        "created_at",
    )
    list_filter = ("plan_code", "start_date", "end_date")
    search_fields = ("organization__name", "plan_code", "subscription_id")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-start_date",)
    autocomplete_fields = ("organization",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "subscription_id",
                    "plan_code",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            "Limits",
            {
                "fields": (
                    "users_limit",
                    "workspaces_limit",
                    "pipeline_runs_limit",
                )
            },
        ),
        (
            "Metadata",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("email",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(ServiceAccount)
class ServiceAccountAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active")
    list_filter = ("is_active",)
    search_fields = ["email"]
    filter_horizontal = ("user_permissions",)
    actions = ["rotate_tokens"]

    fieldsets = (
        (None, {"fields": ("email",)}),
        ("Permissions", {"fields": ("is_active", "user_permissions")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.token_hash:
            raw_token = obj.generate_token()
            obj._raw_token = raw_token
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        if hasattr(obj, "_raw_token"):
            self.message_user(
                request,
                mark_safe(
                    f"Token created (will NOT be shown again): <code>{obj._raw_token}</code>"
                    f"<script>prompt('Copy this token (it will NOT be shown again):', '{obj._raw_token}');</script>"
                ),
                messages.SUCCESS,
            )
        return super().response_add(request, obj, post_url_continue)

    @admin.action(description="Rotate tokens (new tokens shown once)")
    def rotate_tokens(self, request, queryset):
        for svc in queryset:
            token = svc.rotate_token()
            self.message_user(
                request,
                mark_safe(
                    f"Token for {svc.email} (will NOT be shown again): <code>{token}</code>"
                    f"<script>prompt('Copy token for {svc.email} (will NOT be shown again):', '{token}');</script>"
                ),
                messages.SUCCESS,
            )
