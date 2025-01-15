import typing
import uuid

import stringcase
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.validators import validate_slug
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from slugify import slugify

from hexa.core.models.base import BaseQuerySet
from hexa.core.models.cryptography import EncryptedTextField
from hexa.user_management.models import User


class ConnectionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self._filter_for_user_and_query_object(
                user,
                Q(workspace=user.pipeline_run.pipeline.workspace),
                return_all_if_superuser=False,
            )
        else:
            return self._filter_for_user_and_query_object(
                user, Q(workspace__members=user), return_all_if_superuser=False
            )


class ConnectionManager(models.Manager):
    from hexa.workspaces.models import (
        Workspace,  # Lazy import to avoid circular imports
    )

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

        # Check if the slug does not already exist
        if not slug:
            slug = slugify(name)[:40].rstrip("-")

        if self.filter(workspace=workspace, slug=slug).exists():
            # If the slug already exists, we add a random string to it
            slug = f"{slug}-{uuid.uuid4().hex[:4]}"

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
    IASO = "IASO", _("IASO Instance")


class Connection(models.Model):
    db_table = "workspaces_connection"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "workspaces.Workspace", on_delete=models.CASCADE, related_name="connections"
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

    def __str__(self) -> str:
        return self.slug

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                "workspace",
                "slug",
                name="connection_unique_workspace_connection_slug",
            )
        ]

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
        env = {f.env_key: f.value for f in self.fields.all()}

        if self.connection_type == ConnectionType.IASO:
            fields = {f.code: f.value for f in self.fields.all()}
            env.update(
                {
                    # Add "_API_URL" for backward-compatibility (we now use "_URL" but it used to be _API_URL")
                    stringcase.constcase(f"{self.slug}_api_url".lower()): fields["url"]
                }
            )
        if self.connection_type == ConnectionType.POSTGRESQL:
            fields = {f.code: f.value for f in self.fields.all()}
            env.update(
                {
                    # Add compound database URL for SQLALchemy and the like
                    stringcase.constcase(
                        f"{self.slug}_url".lower()
                    ): f"postgresql://{fields['username']}:{fields['password']}@{fields['host']}:{fields['port']}/{fields['db_name']}",
                    # Add "_DATABASE" for backward-compatibility (we now use "_DB_NAME" but it used to be _DATABASE")
                    stringcase.constcase(f"{self.slug}_database".lower()): fields[
                        "db_name"
                    ],
                }
            )
        elif self.connection_type == ConnectionType.DHIS2:
            fields = {f.code: f.value for f in self.fields.all()}
            env.update(
                {
                    # Add "_API_URL" for backward-compatibility (we now use "_URL" but it used to be _API_URL")
                    stringcase.constcase(f"{self.slug}_api_url".lower()): fields["url"]
                }
            )
        return env


class ConnectionField(models.Model):
    db_table = "workspaces_connectionfield"

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
        return stringcase.constcase(f"{self.connection.slug}_{self.code}".lower())

    class Meta:
        unique_together = [["connection", "code"]]
        ordering = ("created_at",)
