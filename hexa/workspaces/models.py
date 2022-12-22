import typing
import uuid

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country, CountryField

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.user_management.models import User


class WorkspaceManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        name: str,
        description: str,
        countries: typing.Sequence[Country] = None
    ):
        if not principal.has_perm("workspaces.create_workspace"):
            raise PermissionDenied

        create_kwargs = {"name": name, "description": description}
        if countries is not None:
            create_kwargs["countries"] = countries

        workspace = self.create(**create_kwargs)
        WorkspaceMembership.objects.create(
            user=principal, workspace=workspace, role=WorkspaceMembershipRole.ADMIN
        )

        return workspace


class WorkspaceQuerySet(BaseQuerySet):
    def filter_for_user(
        self, user: typing.Union[AnonymousUser, User]
    ) -> models.QuerySet:
        return self._filter_for_user_and_query_object(user, Q(members=user))


class Workspace(Base):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    description = models.TextField(blank=True)
    members = models.ManyToManyField(
        "user_management.User",
        through="WorkspaceMembership",
        related_name="workspace_members",
    )
    countries = CountryField(multiple=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "user_management.User",
        null=True,
        on_delete=models.SET_NULL,
    )
    objects = WorkspaceManager.from_queryset(WorkspaceQuerySet)()


class WorkspaceMembershipRole(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    EDITOR = "EDITOR", _("Editor")
    VIEWER = "VIEWER", _("Viewer")


class WorkspaceMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "user_management.User",
        on_delete=models.CASCADE,
    )
    role = models.CharField(choices=WorkspaceMembershipRole.choices, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
