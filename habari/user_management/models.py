from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from habari.common.models import Descriptive


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


class OrganizationType(models.TextChoices):
    CORPORATE = "CORPORATE", _("Corporate")
    ACADEMIC = "ACADEMIC", _("Academic")
    GOVERNMENT = "GOVERNMENT", _("Government")
    NGO = "NGO", _("Non-governmental")


class Organization(Descriptive):
    organization_type = models.CharField(
        choices=OrganizationType.choices, max_length=100
    )
    url = models.URLField(blank=True)
    contact_info = models.TextField(blank=True)
