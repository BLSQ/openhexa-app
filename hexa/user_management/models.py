from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models import EmailField, Q
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet


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
        try:  # Always return True for "forced-activated features"
            Feature.objects.get(code=code, force_activate=True)

            return True
        except Feature.DoesNotExist:
            return self.featureflag_set.filter(feature__code=code).exists()

    def is_member_of(self, team):
        return self.membership_set.filter(team=team).exists()

    def is_admin_of(self, team):
        return self.membership_set.filter(team=team, role=MembershipRole.ADMIN).exists()

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip() + f" ({self.email})"

        return self.email


class OrganizationType(models.TextChoices):
    CORPORATE = "CORPORATE", _("Corporate")
    ACADEMIC = "ACADEMIC", _("Academic")
    GOVERNMENT = "GOVERNMENT", _("Government")
    NGO = "NGO", _("Non-governmental")


class Organization(Base):
    class Meta:
        db_table = "identity_organization"

    organization_type = models.CharField(
        choices=OrganizationType.choices, max_length=100
    )
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    url = models.URLField(blank=True)
    contact_info = models.TextField(blank=True)


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
