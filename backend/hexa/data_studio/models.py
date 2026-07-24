import secrets

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models
from slugify import slugify

from hexa.core.models.base import Base, BaseQuerySet
from hexa.data_studio.execution import validate_parameters_spec
from hexa.user_management.models import User, UserInterface
from hexa.workspaces.models import Workspace


def create_saved_query_slug(name: str, workspace: Workspace) -> str:
    """Generate a unique slug for a saved query within a workspace."""
    suffix = ""
    while True:
        slug = slugify(name[: 255 - len(suffix)] + suffix)
        if not SavedQuery.objects.filter(workspace=workspace, slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)


class SavedQueryQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        return self.filter(workspace__in=Workspace.objects.filter_for_user(user))


class SavedQueryManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: Workspace,
        *,
        name: str,
        content: str,
        description: str = "",
        parameters: list | None = None,
        is_public: bool = False,
    ):
        if not principal.has_perm("data_studio.create_saved_query", workspace):
            raise PermissionDenied

        if is_public and not principal.has_perm(
            "data_studio.publish_saved_query", workspace
        ):
            raise PermissionDenied

        parameters = parameters or []
        validate_parameters_spec(parameters)

        return self.create(
            workspace=workspace,
            created_by=principal,
            name=name,
            content=content,
            description=description,
            slug=create_saved_query_slug(name, workspace),
            parameters=parameters,
            is_public=is_public,
        )


class SavedQuery(Base):
    """A SQL query saved by a user in the Data Studio, shared with the whole workspace."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="saved_queries",
    )
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    parameters = models.JSONField(default=list, blank=True)

    objects = SavedQueryManager.from_queryset(SavedQueryQuerySet)()

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "slug"],
                name="data_studio_ws_slug_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["workspace", "-updated_at"],
                name="data_studio_ws_updated_idx",
            ),
            models.Index(
                fields=["workspace", "slug"],
                name="data_studio_ws_slug_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("data_studio.update_saved_query", self):
            raise PermissionDenied

        if (
            kwargs.get("is_public") is not None
            and kwargs["is_public"] != self.is_public
        ):
            if not principal.has_perm(
                "data_studio.publish_saved_query", self.workspace
            ):
                raise PermissionDenied
            self.is_public = kwargs["is_public"]

        for key in ["name", "content"]:
            if kwargs.get(key) is not None:
                setattr(self, key, kwargs[key])

        # description is optional/blankable: an explicit null clears it, mirroring create.
        if "description" in kwargs:
            self.description = kwargs["description"] or ""

        if kwargs.get("parameters") is not None:
            validate_parameters_spec(kwargs["parameters"])
            self.parameters = kwargs["parameters"]

        return self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("data_studio.delete_saved_query", self):
            raise PermissionDenied

        return self.delete()
