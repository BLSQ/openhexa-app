from __future__ import annotations

import base64
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.signing import TimestampSigner
from django.db import models
from django.db.models import EmailField, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email=None, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email or not password:
            raise ValueError(_("Email and password must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        if not email or not password:
            raise ValueError(_("Email and password must be set"))

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class UserInterface:
    is_staff = False
    is_active = False
    is_superuser = False
    is_anonymous = True

    def has_perm(self, perm, obj=None):
        raise NotImplementedError

    def get_username(self):
        raise NotImplementedError

    @property
    def is_authenticated(self):
        return False


class User(AbstractUser, UserInterface):
    class Meta:
        db_table = "identity_user"
        ordering = ["last_name"]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = EmailField(_("email address"), db_collation="case_insensitive", unique=True)
    language = models.CharField(max_length=10, default="en")
    analytics_enabled = models.BooleanField(default=True)

    objects = UserManager()

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()

        return self.email

    @property
    def initials(self):
        if self.first_name != "" and self.last_name != "":
            return f"{self.first_name[0]}{self.last_name[0]}".upper()

        return self.email[:2].upper()

    def has_feature_flag(self, code: str) -> bool:
        return (
            Feature.objects.are_enabled_for_user(user=self).filter(code=code).exists()
        )

    def is_member_of(self, team):
        return self.membership_set.filter(team=team).exists()

    def is_admin_of(self, team):
        return self.membership_set.filter(team=team, role=MembershipRole.ADMIN).exists()

    def is_organization_member(self, organization: Organization | None):
        """Check if user is a member of the organization (any role)"""
        return (
            organization is not None
            and self.organizationmembership_set.filter(
                organization=organization
            ).exists()
        )

    def is_organization_admin_or_owner(self, organization: Organization | None):
        """Check if user has admin or owner privileges in the organization"""
        return (
            organization is not None
            and self.organizationmembership_set.filter(
                organization=organization,
                role__in=[
                    OrganizationMembershipRole.ADMIN,
                    OrganizationMembershipRole.OWNER,
                ],
            ).exists()
        )

    def is_organization_owner(self, organization: Organization | None):
        """Check if user is an owner of the organization"""
        return (
            organization is not None
            and self.organizationmembership_set.filter(
                organization=organization,
                role=OrganizationMembershipRole.OWNER,
            ).exists()
        )

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip() + f" ({self.email})"

        return self.email


class OrganizationType(models.TextChoices):
    CORPORATE = "CORPORATE", _("Corporate")
    ACADEMIC = "ACADEMIC", _("Academic")
    GOVERNMENT = "GOVERNMENT", _("Government")
    NGO = "NGO", _("Non-governmental")


class OrganizationManager(models.Manager):
    pass


class OrganizationQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self._filter_for_user_and_query_object(
                user,
                models.Q(workspaces=user.pipeline_run.pipeline.workspace),
            )
        return self._filter_for_user_and_query_object(
            user,
            Q(organizationmembership__user=user),
            return_all_if_superuser=True,
        )


class Organization(Base, SoftDeletedModel):
    class Meta:
        db_table = "identity_organization"

    organization_type = models.CharField(
        choices=OrganizationType.choices, max_length=100
    )
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=100, blank=True, unique=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    url = models.URLField(blank=True)
    contact_info = models.TextField(blank=True)
    logo = models.BinaryField(blank=True, null=True)
    members = models.ManyToManyField(User, through="OrganizationMembership")

    objects = DefaultSoftDeletedManager.from_queryset(OrganizationQuerySet)()
    all_objects = IncludeSoftDeletedManager.from_queryset(OrganizationQuerySet)()

    def delete(self):
        """
        Soft delete the organization and archive all related workspaces.
        """
        super().delete()
        self.workspaces.filter(archived=False).update(
            archived=True, archived_at=timezone.now()
        )

    def restore(self):
        """
        Restore the organization and unarchive workspaces that were archived
        at the same time as the organization deletion.
        """
        if self.deleted_at:
            time_threshold = self.deleted_at - timedelta(seconds=2)
            self.workspaces.filter(
                archived=True, archived_at__gte=time_threshold
            ).update(archived=False, archived_at=None)
        super().restore()

    def filter_workspaces_for_user(self, user):
        workspaces = self.workspaces.exclude(archived=True)
        if user.has_perm("user_management.has_admin_privileges", self):
            return workspaces
        return workspaces.filter(members=user)

    @property
    def active_subscription(self):
        """
        Returns the currently active subscription based on today's date.
        Returns None if no subscription exists (self-hosted mode).
        """
        today = timezone.now().date()
        return self.subscriptions.filter(
            subscription_start_date__lte=today,
            subscription_end_date__gte=today,
        ).first()

    @property
    def pending_subscription(self):
        """
        Returns the next pending subscription (if any).
        Used for downgrades that take effect at end of billing period.
        """
        today = timezone.now().date()
        return (
            self.subscriptions.filter(
                subscription_start_date__gt=today,
            )
            .order_by("subscription_start_date")
            .first()
        )

    def get_users_count(self) -> int:
        """Count organization members."""
        return (
            self.organizationmembership_set.count()
        )  # TODO: this does not consider workspace-only users

    def get_workspaces_count(self) -> int:
        """Count active (non-archived) workspaces."""
        return self.workspaces.filter(archived=False).count()

    def get_monthly_pipeline_runs_count(self) -> int:
        """Count pipeline runs for the current calendar month."""
        from hexa.pipelines.models import PipelineRun

        today = timezone.now().date()
        month_start = today.replace(day=1)  # TODO: should we consider start date ?
        return PipelineRun.objects.filter(
            pipeline__workspace__organization=self,
            created_at__date__gte=month_start,
        ).count()

    def is_users_limit_reached(self) -> bool:
        """Check if the organization has reached its user limit."""
        subscription = self.active_subscription
        return subscription.is_users_limit_reached() if subscription else False

    def is_workspaces_limit_reached(self) -> bool:
        """Check if the organization has reached its workspace limit."""
        subscription = self.active_subscription
        return subscription.is_workspaces_limit_reached() if subscription else False

    def is_pipeline_runs_limit_reached(self) -> bool:
        """Check if the organization has reached its pipeline runs limit."""
        subscription = self.active_subscription
        return subscription.is_pipeline_runs_limit_reached() if subscription else False


class OrganizationSubscription(Base):
    """
    Stores SaaS subscription information for an organization.
    Created and managed by the Bluesquare Console via GraphQL mutations.

    An organization can have multiple subscriptions (current + pending).
    Use organization.active_subscription to get the currently active one.

    Self-hosted deployments have no subscription (active_subscription returns None).
    """

    class Meta:
        db_table = "identity_organization_subscription"
        ordering = ["-subscription_start_date"]  # Most recent first

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    subscription_id = models.UUIDField(
        unique=True
    )  # External subscription ID from the Bluesquare Console
    plan_code = models.CharField(max_length=100)
    subscription_start_date = models.DateField()
    subscription_end_date = models.DateField()

    users_limit = models.PositiveIntegerField()
    workspaces_limit = models.PositiveIntegerField()
    pipeline_runs_limit = models.PositiveIntegerField()

    def is_users_limit_reached(self) -> bool:
        """Check if the organization has reached its user limit."""
        return self.organization.get_users_count() >= self.users_limit

    def is_workspaces_limit_reached(self) -> bool:
        """Check if the organization has reached its workspace limit."""
        return self.organization.get_workspaces_count() >= self.workspaces_limit

    def is_pipeline_runs_limit_reached(self) -> bool:
        """Check if the organization has reached its monthly pipeline runs limit."""
        return (
            self.organization.get_monthly_pipeline_runs_count()
            >= self.pipeline_runs_limit
        )


class OrganizationMembershipRole(models.TextChoices):
    OWNER = "owner", _("Owner")
    ADMIN = "admin", _("Admin")
    MEMBER = "member", _("Member")


class OrganizationMembership(Base):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="organization_membership_unique_organization_user",
            )
        ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "user_management.User",
        on_delete=models.CASCADE,
    )
    role = models.CharField(choices=OrganizationMembershipRole.choices, max_length=50)

    @classmethod
    def create_if_has_perm(
        cls,
        principal: User,
        *,
        organization: Organization,
        user: User,
        role: OrganizationMembershipRole,
    ):
        if not principal.has_perm("user_management.manage_members", organization):
            raise PermissionDenied

        if role == OrganizationMembershipRole.OWNER:
            if not principal.has_perm("user_management.manage_owners", organization):
                raise PermissionDenied

        return cls.objects.create(
            organization=organization,
            user=user,
            role=role,
        )

    def update_if_has_perm(self, *, principal: User, role: OrganizationMembershipRole):
        if not principal.has_perm("user_management.manage_members", self.organization):
            raise PermissionDenied
        if (
            principal.id == self.user.id
            or self.role == OrganizationMembershipRole.OWNER
        ):
            raise PermissionDenied

        if role == OrganizationMembershipRole.OWNER:
            if not principal.has_perm(
                "user_management.manage_owners", self.organization
            ):
                raise PermissionDenied

        self.role = role
        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("user_management.manage_members", self.organization):
            raise PermissionDenied
        if principal.id == self.user.id:
            raise PermissionDenied

        if self.role == OrganizationMembershipRole.OWNER:
            if not principal.has_perm(
                "user_management.manage_owners", self.organization
            ):
                raise PermissionDenied

        return self.delete()


class TeamManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        name: str,
    ):
        if not principal.has_perm("user_management.create_team"):
            raise PermissionDenied

        team = self.create(name=name)
        Membership.objects.create_if_has_perm(
            principal=principal, user=principal, team=team, role=MembershipRole.ADMIN
        )

        return team


class TeamQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        return self._filter_for_user_and_query_object(user, Q(members=user))


class Team(Base):
    class Meta:
        db_table = "identity_team"
        ordering = ["name"]

    name = models.CharField(max_length=200, unique=True)
    members = models.ManyToManyField("User", through="Membership")

    objects = TeamManager.from_queryset(TeamQuerySet)()

    def update_if_has_perm(self, principal: User, *, name: str):
        if not principal.has_perm("user_management.update_team", self):
            raise PermissionDenied

        self.name = name
        self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("user_management.delete_team", self):
            raise PermissionDenied

        return super().delete()


class MembershipRole(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    REGULAR = "REGULAR", _("Regular")


class MembershipError(Exception):
    pass


class AlreadyExists(MembershipError):
    pass


class CannotDowngradeRole(MembershipError):
    pass


class CannotDelete(MembershipError):
    pass


class MembershipManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        user: User,
        team: Team,
        role: MembershipRole | None = MembershipRole.REGULAR,
    ):
        if not principal.has_perm("user_management.create_membership", team):
            raise PermissionDenied

        if Membership.objects.filter(user=user, team=team).exists():
            raise AlreadyExists(
                f"Already got a membership for user {user.id} and team {team.name}"
            )

        return self.create(user=user, team=team, role=role)


class MembershipQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        return self._filter_for_user_and_query_object(user, Q(team__members=user))


class Membership(Base):
    class Meta:
        db_table = "identity_membership"
        ordering = ["team__name", "user__email"]
        constraints = [
            models.UniqueConstraint("user", "team", name="membership_unique_user_team")
        ]

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=200, choices=MembershipRole.choices, default=MembershipRole.REGULAR
    )

    objects = MembershipManager.from_queryset(MembershipQuerySet)()

    @property
    def display_name(self):
        return f"{self.user.display_name} / {self.team.display_name}"

    def update_if_has_perm(self, principal: User, *, role: MembershipRole):
        if not principal.has_perm("user_management.update_membership", self):
            raise PermissionDenied

        if self.user == principal and self.role == MembershipRole.ADMIN:
            raise CannotDowngradeRole(f"User {principal} cannot downgrade its role")

        self.role = role
        self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("user_management.delete_membership", self):
            raise PermissionDenied

        if self.user == principal:
            raise CannotDelete(f"User {principal.id} cannot delete herself")

        return super().delete()


class FeatureManager(models.Manager):
    def get_by_natural_key(self, code: str):
        return self.get(code=code)

    def are_enabled_for_user(self, user: User) -> list[Feature]:
        return self.filter(
            Q(force_activate=True)
            | Q(code__in=user.featureflag_set.values_list("feature__code", flat=True))
        )


class Feature(Base):
    class Meta:
        db_table = "identity_feature"

    code = models.CharField(max_length=200)
    force_activate = models.BooleanField(default=False)

    def natural_key(self):
        return (self.code,)

    objects = FeatureManager()

    def __str__(self):
        return self.code


class FeatureFlag(Base):
    class Meta:
        db_table = "identity_featureflag"

    feature = models.ForeignKey("Feature", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    config = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return f"{self.feature.code} - {self.user.display_name}"


class PermissionMode(models.TextChoices):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


class Permission(Base):
    class Meta:
        abstract = True

    team = models.ForeignKey(
        "user_management.Team", null=True, on_delete=models.CASCADE, blank=True
    )
    user = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.CASCADE, blank=True
    )
    index_permission = GenericRelation(
        "catalog.IndexPermission",
        content_type_field="permission_type_id",
        object_id_field="permission_id",
    )
    mode = models.CharField(
        max_length=200, choices=PermissionMode.choices, default=PermissionMode.EDITOR
    )

    def clean(self):
        if (self.team is None) == (self.user is None):
            raise ValidationError("Only one of team or user should be provided")

    def save(self, *args, **kwargs):
        if (self.team is None) == (self.user is None):
            raise ValueError("Only one of team or user should be provided")

        super().save(*args, **kwargs)
        self.index_object()

    def index_object(self):
        raise NotImplementedError


class OrganizationInvitationStatus(models.TextChoices):
    PENDING = "PENDING"
    DECLINED = "DECLINED"
    ACCEPTED = "ACCEPTED"


class OrganizationInvitationQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user,
            Q(organization__organizationmembership__user=user),
            return_all_if_superuser=False,
        )


class OrganizationInvitationManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        organization: Organization,
        email: str,
        role: OrganizationMembershipRole,
        workspace_invitations: list = None,
    ):
        if not principal.has_perm("user_management.manage_members", organization):
            raise PermissionDenied

        if role == OrganizationMembershipRole.OWNER:
            if not principal.has_perm("user_management.manage_owners", organization):
                raise PermissionDenied

        invitation = self.create(
            email=email,
            organization=organization,
            role=role,
            invited_by=principal,
        )

        if workspace_invitations:
            from hexa.workspaces.models import OrganizationWorkspaceInvitation

            OrganizationWorkspaceInvitation.create_invitations_for_organization_invitation(
                invitation, workspace_invitations
            )

        return invitation

    def get_by_token(self, token: str):
        signer = TimestampSigner()
        decoded_value = base64.b64decode(token).decode("utf-8")
        # the token is valid for 48h
        invitation_id = signer.unsign(decoded_value, max_age=48 * 3600)
        return self.get(id=invitation_id)


class OrganizationInvitation(Base):
    email = EmailField(db_collation="case_insensitive")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
    )
    invited_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
    )
    role = models.CharField(choices=OrganizationMembershipRole.choices, max_length=50)
    status = models.CharField(
        max_length=50,
        choices=OrganizationInvitationStatus.choices,
        default=OrganizationInvitationStatus.PENDING,
    )

    objects = OrganizationInvitationManager.from_queryset(
        OrganizationInvitationQuerySet
    )()

    def generate_invitation_token(self):
        signer = TimestampSigner()
        return base64.b64encode(signer.sign(self.id).encode("utf-8")).decode()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("user_management.manage_members", self.organization):
            raise PermissionDenied

        return self.delete()
