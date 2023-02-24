import secrets
import typing
import uuid

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.validators import RegexValidator, validate_slug
from django.db import models
from django.db.models import Q
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country, CountryField
from slugify import slugify

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.cryptography import EncryptedTextField
from hexa.databases.api import create_database, format_db_name
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
        description: str = None,
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

        password = User.objects.make_random_password()
        db_name = format_db_name(create_kwargs["slug"])

        create_kwargs["db_password"] = password
        create_kwargs["db_name"] = db_name

        create_database(db_name, password)

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

    db_name = models.TextField(null=True)
    db_password = EncryptedTextField(null=True)

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


class ConnectionQuerySet(BaseQuerySet):
    def filter_for_user(
        self, user: typing.Union[AnonymousUser, User]
    ) -> models.QuerySet:
        return self._filter_for_user_and_query_object(user, Q(workspace__members=user))


class ConnectionManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: Workspace,
        name,
        fields=None,
        slug=None,
        **kwargs,
    ):
        if not principal.has_perm("workspaces.create_connection", workspace):
            raise PermissionDenied

        if not slug:
            slug = slugify(name)[:100]

        connection = Connection(
            workspace=workspace, user=principal, name=name, slug=slug, **kwargs
        )
        connection.full_clean()
        connection.save()
        if fields is not None:
            connection.set_fields(principal, fields)

        return connection


class ConnectionType(models.TextChoices):
    S3 = "S3", _("S3 Bucket")
    GCS = "GCS", _("GCS Bucket")
    POSTGRESQL = "POSTGRESQL", _("PostgreSQL DB")
    CUSTOM = "CUSTOM", _("Custom")
    DHIS2 = "DHIS2", _("DHIS2 Instance")


class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="connections"
    )
    user = models.ForeignKey(
        "user_management.User",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255, null=False)
    slug = models.CharField(max_length=100, null=False, validators=[validate_slug])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    connection_type = models.TextField(
        choices=ConnectionType.choices, max_length=32, null=False
    )

    objects = ConnectionManager.from_queryset(ConnectionQuerySet)()

    class Meta:
        ordering = ["-updated_at"]

    def set_fields(self, user: User, fields: typing.List[dict]):
        fields_map = {str(f.code): f for f in self.fields.all()}
        for field in fields:

            if field["code"] not in fields_map:
                # Unknown field -> Create it
                current_field = ConnectionField(connection=self, user=user, **field)
            else:
                # Update existing field
                current_field = fields_map[field["code"]]
                for key in ["value", "secret"]:
                    if field[key] is not None:
                        setattr(current_field, key, field[key])
                del fields_map[field["code"]]
            current_field.full_clean()
            current_field.save()

        # Delete all the fields that were not given by the user
        for field_to_delete in fields_map.values():
            field_to_delete.delete()

        return

    def update_if_has_perm(self, principal: User, fields=None, **kwargs):
        if not principal.has_perm("workspaces.update_connection", self):
            raise PermissionDenied

        for key in kwargs:
            setattr(self, key, kwargs[key])

        if fields is not None:
            self.set_fields(principal, fields)

        self.full_clean()
        return self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("workspaces.delete_connection", self):
            raise PermissionDenied

        return self.delete()


class ConnectionField(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(
        Connection, on_delete=models.CASCADE, related_name="fields"
    )
    user = models.ForeignKey(
        "user_management.User",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    code = models.CharField(
        max_length=30, blank=False, null=False, validators=[validate_slug]
    )
    value = EncryptedTextField(blank=True)
    secret = models.BooleanField(default=False)

    class Meta:
        unique_together = [["connection", "code"]]