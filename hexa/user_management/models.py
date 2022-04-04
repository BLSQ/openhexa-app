from __future__ import annotations

import typing
import uuid

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.postgres.fields import CIEmailField
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.plugins.connector_accessmod.permissions import TeamPermissions


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
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = CIEmailField(_("email address"), unique=True)
    accepted_tos = models.BooleanField(default=False)

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

    def __str__(self):
        return self.display_name


class OrganizationType(models.TextChoices):
    CORPORATE = "CORPORATE", _("Corporate")
    ACADEMIC = "ACADEMIC", _("Academic")
    GOVERNMENT = "GOVERNMENT", _("Government")
    NGO = "NGO", _("Non-governmental")


class Organization(Base):
    organization_type = models.CharField(
        choices=OrganizationType.choices, max_length=100
    )
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    url = models.URLField(blank=True)
    contact_info = models.TextField(blank=True)


class MembershipRole(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    REGULAR = "REGULAR", _("Regular")


class TeamManager(models.Manager):
    @staticmethod
    def add_user_to_team(*, principal: User, user: User, team: Team):
        if not principal.has_perm(TeamPermissions.add_user_to_team, [user, team]):
            raise PermissionDenied

        return Membership.objects.create(
            user=user, team=team, role=MembershipRole.REGULAR
        )

    @staticmethod
    def remove_user_from_team(*, principal: User, user: User, team: Team):
        if not principal.has_perm(TeamPermissions.remove_user_from_team, [user, team]):
            raise PermissionDenied

        return Membership.objects.get(
            user=user, team=team, role=MembershipRole.REGULAR
        ).delete()


class TeamQuerySet(BaseQuerySet):
    def filter_for_user(
        self, user: typing.Union[AnonymousUser, User]
    ) -> models.QuerySet:
        return self._filter_for_user_and_query_object(user, Q(members=user))


class Team(Base):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=200)
    members = models.ManyToManyField("User", through="Membership")

    objects = TeamManager.from_queryset(TeamQuerySet)()


class Membership(Base):
    class Meta:
        ordering = ["team__name", "user__email"]

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=200, choices=MembershipRole.choices, default=MembershipRole.REGULAR
    )

    @property
    def display_name(self):
        return f"{self.user.display_name} / {self.team.display_name}"


class Feature(Base):
    code = models.CharField(max_length=200)
    force_activate = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class FeatureFlag(Base):
    feature = models.ForeignKey("Feature", on_delete=models.CharField)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    config = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.feature.code} - {self.user.username}"
