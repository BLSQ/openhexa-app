import secrets
import typing
import uuid

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country, CountryField
from slugify import slugify

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.user_management.models import User


class AlreadyExists(Exception):
    pass


def create_workspace_slug(name):
    suffix = secrets.token_hex(3)
    prefix = slugify(name[:23])
    return prefix[:23] + "-" + suffix


validate_workspace_slug = RegexValidator(
    _lazy_re_compile(r"^[-a-z0-9]+\Z"),
    # Translators: "letters" means latin letters: a-z.
    _("Enter a valid “slug” consisting of letters, numbers or hyphens."),
    "invalid",
)


class WorkspaceManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        name: str,
        description: str,
        countries: typing.Sequence[Country] = None,
    ):
        if not principal.has_perm("workspaces.create_workspace"):
            raise PermissionDenied

        create_kwargs = {"name": name, "description": description}
        create_kwargs["slug"] = create_workspace_slug(name)
        if countries is not None:
            create_kwargs["countries"] = countries
        if description is None:
            create_kwargs["description"] = "This is a workspace for {}".format(name)

        workspace = self.create(**create_kwargs)
        WorkspaceMembership.objects.create(
            user=principal, workspace=workspace, role=WorkspaceMembershipRole.ADMIN
        )

        return workspace


class WorkspaceQuerySet(BaseQuerySet):
    def filter_for_user(
        self, user: typing.Union[AnonymousUser, User]
    ) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user, Q(workspacemembership__user=user)
        )


class Workspace(Base):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    slug = models.CharField(
        max_length=30,
        null=False,
        editable=False,
        validators=[validate_workspace_slug],
        unique=True,
    )
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, through="WorkspaceMembership")
    countries = CountryField(multiple=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "user_management.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="workspace_created_by",
    )
    objects = WorkspaceManager.from_queryset(WorkspaceQuerySet)()

    def update_if_has_perm(self, *, principal: User, **kwargs):
        if not principal.has_perm("workspaces.update_workspace", self):
            raise PermissionDenied

        for key in ["name", "slug", "countries", "description"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("workspaces.delete_workspace", self):
            raise PermissionDenied

        self.delete()


class WorkspaceMembershipQuerySet(BaseQuerySet):
    def filter_for_user(
        self, user: typing.Union[AnonymousUser, User]
    ) -> models.QuerySet:
        return self._filter_for_user_and_query_object(user, Q(user=user))


class WorkspaceMembershipRole(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    EDITOR = "EDITOR", _("Editor")
    VIEWER = "VIEWER", _("Viewer")


class WorkspaceMembershipManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        workspace: Workspace,
        user: User,
        role: WorkspaceMembershipRole,
    ):
        if not principal.has_perm("workspaces.manage_members", workspace):
            raise PermissionDenied

        if WorkspaceMembership.objects.filter(user=user, workspace=workspace).exists():
            raise AlreadyExists(
                f"Already got a membership for user {user.id} and workspace {workspace.name}"
            )

        workspace_membership = self.create(user=user, workspace=workspace, role=role)
        return workspace_membership


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
    objects = WorkspaceMembershipManager.from_queryset(WorkspaceMembershipQuerySet)()

    def update_if_has_perm(self, *, principal: User, role: WorkspaceMembershipRole):
        if not principal.has_perm("workspaces.manage_members", self.workspace):
            raise PermissionDenied

        self.role = role
        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("workspaces.manage_members", self.workspace):
            raise PermissionDenied

        return self.delete()
