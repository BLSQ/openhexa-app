from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
import uuid

from hexa.core.models import Base


class UserManager(BaseUserManager):
    def create_superuser(self, email=None, password=None, **extra_fields):
        """Django does not like users without usernames - at all"""

        return super().create_superuser(email, email, password, **extra_fields)


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        help_text=_("For display purposes only."),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), unique=True)

    objects = UserManager()

    @property
    def display_name(self):
        return self.username

    @property
    def initials(self):
        if self.first_name != "" and self.last_name != "":
            return f"{self.first_name[0]}{self.last_name[0]}".upper()

        return self.username[:2].upper()

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


class Team(Base):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField("User", through="Membership")


class Membership(Base):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)

    @property
    def display_name(self):
        return f"{self.user.display_name} / {self.team.display_name}"
