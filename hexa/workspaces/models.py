import base64
import hashlib
import secrets
import string
import typing
import uuid

import stringcase
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.signing import TimestampSigner
from django.core.validators import RegexValidator, validate_slug
from django.db import models
from django.db.models import EmailField, Q
from django.forms import ValidationError
from django.utils.crypto import get_random_string
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country, CountryField
from slugify import slugify

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.cryptography import EncryptedTextField
from hexa.databases.api import (
    create_database,
    get_db_server_credentials,
    load_database_sample_data,
    update_database_password,
)
from hexa.datasets.models import Dataset
from hexa.files import storage
from hexa.user_management.models import User


class AlreadyExists(Exception):
    pass


def make_random_password(
    length=10, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
):
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def create_workspace_slug(name):
    suffix = ""
    while True:
        slug = slugify(name[: 63 - len(suffix)] + suffix)
        if not Workspace.objects.filter(slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)


def generate_database_name():
    db_name = get_random_string(1, string.ascii_lowercase) + get_random_string(
        15, allowed_chars=string.ascii_lowercase + string.digits
    )

    return db_name


# ease patching
def load_bucket_sample_data(bucket_name):
    storage.load_bucket_sample_data(bucket_name)


validate_workspace_slug = RegexValidator(
    _lazy_re_compile(r"^[-a-z0-9]+\Z"),
    # Translators: "letters" means latin letters: a-z.
    _("Enter a valid “slug” consisting of letters, numbers or hyphens."),
    "invalid",
)


def create_workspace_bucket(workspace_slug: str):
    while True:
        suffix = get_random_string(
            4, allowed_chars=string.ascii_lowercase + string.digits
        )
        try:
            # Bucket names must be unique across all of Google Cloud, so we add a suffix to the workspace slug
            # When separated by a dot, each segment can be up to 63 characters long
            return storage.create_bucket(
                f"{(settings.WORKSPACE_BUCKET_PREFIX + workspace_slug)[:63]}_{suffix}",
                labels={"hexa-workspace": workspace_slug},
            )
        except ValidationError:
            continue


class WorkspaceManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        name: str,
        description: str | None = None,
        countries: typing.Sequence[Country] | None = None,
        load_sample_data: bool = False,
    ):
        if not principal.has_perm("workspaces.create_workspace"):
            raise PermissionDenied

        slug = create_workspace_slug(name)
        create_kwargs = {
            "name": name,
            "description": description,
            "slug": slug,
            "created_by": principal,
        }
        if countries is not None:
            create_kwargs["countries"] = countries
        if description is None:
            create_kwargs["description"] = DEFAULT_WORKSPACE_DESCRIPTION.format(
                workspace_name=name, workspace_slug=slug
            )

        db_password = make_random_password(length=16)
        db_name = generate_database_name()
        create_kwargs["db_password"] = db_password
        create_kwargs["db_name"] = db_name
        create_database(db_name, db_password)

        bucket_name = create_workspace_bucket(slug)
        create_kwargs["bucket_name"] = bucket_name

        if load_sample_data:
            load_database_sample_data(db_name)
            load_bucket_sample_data(bucket_name)

        workspace = self.create(**create_kwargs)

        WorkspaceMembership.objects.create(
            user=principal, workspace=workspace, role=WorkspaceMembershipRole.ADMIN
        )

        return workspace


class WorkspaceQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self._filter_for_user_and_query_object(
                user,
                Q(id=user.pipeline_run.pipeline.workspace.id, archived=False),
                return_all_if_superuser=False,
            )
        else:
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

    db_name = models.CharField(null=False, unique=True, max_length=63)
    db_password = EncryptedTextField(null=False)
    bucket_name = models.TextField(
        null=True,
    )
    archived = models.BooleanField(default=False)
    docker_image = models.TextField(blank=True, default="")
    datasets = models.ManyToManyField(
        Dataset, through="datasets.DatasetLink", related_name="+"
    )

    objects = WorkspaceManager.from_queryset(WorkspaceQuerySet)()

    @property
    def db_host(self):
        return f"{self.slug}.{settings.WORKSPACES_DATABASE_PROXY_HOST}"

    @property
    def db_port(self):
        return get_db_server_credentials()["port"]

    @property
    def db_url(self):
        return f"postgresql://{self.db_name}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    def update_if_has_perm(self, *, principal: User, **kwargs):
        if not principal.has_perm("workspaces.update_workspace", self):
            raise PermissionDenied

        for key in ["name", "slug", "countries", "description", "docker_image"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("workspaces.delete_workspace", self):
            raise PermissionDenied
        # TODO: clarify workspace deletion workflow - buckets are not deleted for now
        # delete_database(self.db_name)
        self.delete()

    def archive_if_has_perm(self, *, principal: User):
        if not principal.has_perm("workspaces.archive_workspace", self):
            raise PermissionDenied
        self.archived = True
        self.save()

    def generate_new_database_password(self, *, principal: User):
        if not principal.has_perm("workspaces.update_workspace", self):
            raise PermissionDenied

        new_password = make_random_password(length=16)
        update_database_password(self.db_name, new_password)

        setattr(self, "db_password", new_password)
        self.save()


class WorkspaceMembershipQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user, Q(workspace__members=user), return_all_if_superuser=False
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
    notebooks_server_hash = models.TextField(
        blank=True,
        unique=True,
        help_text="Can be used to identify a notebook server for a given user and workspace (will be generated automatically)",
        editable=False,
    )
    access_token = models.TextField(
        max_length=50,
        blank=True,
        unique=True,
        help_text="Access token that can be used to interact with the OpenHEXA API (will be generated automatically, set to empty to regenerate a new token)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = WorkspaceMembershipManager.from_queryset(WorkspaceMembershipQuerySet)()

    def save(self, *args, **kwargs):
        if self.notebooks_server_hash == "":
            self.notebooks_server_hash = hashlib.blake2s(
                f"{self.workspace_id}_{self.user_id}".encode(), digest_size=16
            ).hexdigest()

        if self.access_token == "":
            self.access_token = uuid.uuid4()

        super().save(*args, **kwargs)

    def update_if_has_perm(self, *, principal: User, role: WorkspaceMembershipRole):
        if not principal.has_perm("workspaces.manage_members", self.workspace):
            raise PermissionDenied
        # user cannot update his role
        if principal.id == self.user.id:
            raise PermissionDenied

        self.role = role
        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("workspaces.manage_members", self.workspace):
            raise PermissionDenied
        # user cannot delete his membership
        if principal.id == self.user.id:
            raise PermissionDenied

        return self.delete()


class WorkspaceInvitationStatus(models.TextChoices):
    PENDING = "PENDING"
    DECLINED = "DECLINED"
    ACCEPTED = "ACCEPTED"


class WorkspaceInvitationQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user, Q(workspace__members=user), return_all_if_superuser=False
        )


class WorkspaceInvitationManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        workspace: Workspace,
        email: string,
        role: WorkspaceMembershipRole,
    ):
        if not principal.has_perm("workspaces.manage_members", workspace):
            raise PermissionDenied

        return self.create(
            email=email, workspace=workspace, role=role, invited_by=principal
        )

    def get_by_token(self, token: string):
        signer = TimestampSigner()
        decoded_value = base64.b64decode(token).decode("utf-8")
        # the token is valid for 48h
        invitation_id = signer.unsign(decoded_value, max_age=48 * 3600)
        return self.get(id=invitation_id)


class WorkspaceInvitation(Base):
    email = EmailField(db_collation="case_insensitive")
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
    )
    invited_by = models.ForeignKey(
        "user_management.User",
        null=True,
        on_delete=models.SET_NULL,
    )
    role = models.CharField(choices=WorkspaceMembershipRole.choices, max_length=50)
    status = models.CharField(
        max_length=50,
        choices=WorkspaceInvitationStatus.choices,
        default=WorkspaceInvitationStatus.PENDING,
    )

    objects = WorkspaceInvitationManager.from_queryset(WorkspaceInvitationQuerySet)()

    def generate_invitation_token(self):
        signer = TimestampSigner()
        return base64.b64encode(signer.sign(self.id).encode("utf-8")).decode()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("workspaces.manage_members", self.workspace):
            raise PermissionDenied

        return self.delete()


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


DEFAULT_WORKSPACE_DESCRIPTION = """# {workspace_name}

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
- Manage users and permissions [notebooks](/workspaces/{workspace_slug}/settings)"""
