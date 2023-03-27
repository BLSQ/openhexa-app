import hashlib
import secrets
import typing
import uuid

import stringcase
from django.conf import settings
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
from hexa.databases.api import (
    create_database,
    delete_database,
    format_db_name,
    load_database_sample_data,
    update_database_password,
)
from hexa.files.api import create_bucket, load_bucket_sample_data
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
        name: str,
        description: str = None,
        countries: typing.Sequence[Country] = None,
    ):
        if not principal.has_perm("workspaces.create_workspace"):
            raise PermissionDenied

        slug = create_workspace_slug(name)
        create_kwargs = {"name": name, "description": description, "slug": slug}
        if countries is not None:
            create_kwargs["countries"] = countries
        if description is None:
            create_kwargs["description"] = DEFAULT_WORKSPACE_DESCRIPTION.format(
                workspace_name=name, workspace_slug=slug
            )

        db_password = User.objects.make_random_password(length=16)
        db_name = format_db_name(
            hashlib.blake2s(slug.encode("utf-8"), digest_size=16).hexdigest()
        )

        create_kwargs["db_password"] = db_password
        create_kwargs["db_name"] = db_name

        create_database(db_name, db_password)
        load_database_sample_data(db_name)

        bucket = create_bucket(settings.WORKSPACE_BUCKET_PREFIX + slug)
        load_bucket_sample_data(bucket.name)
        create_kwargs["bucket_name"] = bucket.name

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
            user,
            Q(workspacemembership__user=user, archived=False),
            return_all_if_superuser=False,
        )


class Workspace(Base):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    slug = models.CharField(
        max_length=63,
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
    bucket_name = models.TextField(
        null=True,
    )
    archived = models.BooleanField(default=False)

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
        delete_database(self.db_name)
        self.delete()

    def archive_if_has_perm(self, *, principal: User):
        if not principal.has_perm("workspaces.archive_workspace", self):
            raise PermissionDenied
        self.archived = True
        self.save()

    def generate_new_database_password(self, *, principal: User):
        if not principal.has_perm("workspaces.update_workspace", self):
            raise PermissionDenied

        new_password = User.objects.make_random_password(length=16)
        update_database_password(self.db_name, new_password)

        setattr(self, "db_password", new_password)
        self.save()


class WorkspaceMembershipQuerySet(BaseQuerySet):
    def filter_for_user(
        self, user: typing.Union[AnonymousUser, User]
    ) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user, Q(user=user), return_all_if_superuser=False
        )


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

        workspace_membership = self.create(
            user=user,
            workspace=workspace,
            role=role,
        )
        return workspace_membership


class WorkspaceMembership(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                "workspace",
                "user",
                name="workspace_membership_unique_workspace_user",
            )
        ]

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
    notebooks_server_hash = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = WorkspaceMembershipManager.from_queryset(WorkspaceMembershipQuerySet)()

    def save(self, *args, **kwargs):
        if self.notebooks_server_hash == "":
            self.notebooks_server_hash = hashlib.blake2s(
                f"{self.workspace_id}_{self.user_id}".encode("utf-8"), digest_size=16
            ).hexdigest()

        super().save(*args, **kwargs)

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
        return self._filter_for_user_and_query_object(
            user, Q(workspace__members=user), return_all_if_superuser=False
        )


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

    @property
    def env_variables(self):
        return {f.env_key: f.value for f in self.fields.all()}


class ConnectionField(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(
        Connection, on_delete=models.CASCADE, related_name="fields"
    )
    user = models.ForeignKey(
        "user_management.User", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    code = models.CharField(
        max_length=30, blank=False, null=False, validators=[validate_slug]
    )
    value = EncryptedTextField(blank=True)
    secret = models.BooleanField(default=False)

    @property
    def env_key(self):
        return f"{stringcase.constcase(self.connection.slug)}_{self.code}"

    class Meta:
        unique_together = [["connection", "code"]]


DEFAULT_WORKSPACE_DESCRIPTION = """
# {workspace_name}

Welcome to your new workspace "{workspace_name}"!

You are currently viewing the homepage of your workspace. This page can be edited by workspace administrators and
editors simply by clicking the **Edit** button on the top-right corner of this screen.

This page must be formatted using [Markdown syntax](https://www.markdownguide.org/cheat-sheet/).

This page is meant to serve as the landing page of your projet. You can use it to document to document your project, by:

- Adding a few words of introduction to **describe the purpose of your workspace**
- Explaining **what data** resides in this workspace and **how this data is being used**
- Documenting the main **data pipelines** of the workspace
- Add **external links** to visualization dashboards related to this workspace

## Where to go from here?

Now that your workspace has been created, you can (depending on your privileges):

- Manage the [workspace files](/workspaces/{workspace_slug}/files)
- Browse the [workspace database](/workspaces/{workspace_slug}/databases)
- Create and run code [notebooks](/workspaces/{workspace_slug}/notebooks)
- Monitor and launch [data pipelines](/workspaces/{workspace_slug}/pipelines)
- Manage users and permissions [notebooks](/workspaces/{workspace_slug}/settings)
"""
