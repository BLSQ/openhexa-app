import secrets

from django.contrib.auth.models import AnonymousUser
from django.core.validators import validate_slug
from django.db import models
from django.db.models import Q
from slugify import slugify

from hexa.core.models.base import Base, BaseManager, BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.shortcuts.mixins import ShortcutableMixin
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


def create_webapp_slug(name: str, workspace):
    """Generate a unique slug for a webapp within a workspace.

    Uses the webapp name to generate a slug, truncating to 40 characters
    and adding a random suffix if there's a collision.
    """
    suffix = ""
    while True:
        # Truncate to 40 chars to leave room for potential suffix
        base_slug = slugify(name)[:40].rstrip("-")
        slug = base_slug + suffix

        # Check if slug already exists in this workspace
        if not Webapp.objects.filter(workspace=workspace, slug=slug).exists():
            return slug

        # Add random suffix for collision handling (6 hex characters)
        suffix = "-" + secrets.token_hex(3)


class WebappQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self._filter_for_user_and_query_object(
                user,
                models.Q(workspace=user.pipeline_run.pipeline.workspace),
            )
        return self._filter_for_user_and_query_object(
            user,
            Q(workspace__members=user),
            return_all_if_superuser=False,
            return_all_if_organization_admin_or_owner=True,
        )

    def filter_favorites(self, user: User):
        return self.filter(favorites=user)


class WebappManager(
    BaseManager, DefaultSoftDeletedManager.from_queryset(WebappQuerySet)
):
    def create_if_has_perm(self, principal, ws, **kwargs):
        """Create a webapp with an auto-generated slug."""
        from django.core.exceptions import PermissionDenied

        if not principal.has_perm(
            f"{self.model._meta.app_label}.create_{self.model._meta.model_name}", ws
        ):
            raise PermissionDenied

        # Generate slug from name if not provided
        if "slug" not in kwargs:
            kwargs["slug"] = create_webapp_slug(kwargs["name"], kwargs["workspace"])

        return super(BaseManager, self).create(**kwargs)


class AllWebappManager(
    BaseManager, IncludeSoftDeletedManager.from_queryset(WebappQuerySet)
):
    pass


class Webapp(Base, SoftDeletedModel, ShortcutableMixin):
    class Meta:
        verbose_name = "Webapp"
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "name",
                name="unique_webapp_name_per_workspace",
                condition=Q(deleted_at__isnull=True),
            ),
            models.UniqueConstraint(
                "workspace_id",
                "slug",
                name="unique_webapp_slug_per_workspace",
                condition=Q(deleted_at__isnull=True),
            ),
        ]

    name = models.CharField(max_length=255)
    slug = models.CharField(
        max_length=100, null=False, editable=False, validators=[validate_slug]
    )
    description = models.TextField(blank=True)
    icon = models.BinaryField(blank=True, null=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="webapps"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    favorites = models.ManyToManyField(
        User, related_name="favorite_webapps", blank=True
    )
    objects = WebappManager()
    all_objects = AllWebappManager()

    def is_favorite(self, user: User):
        return self.favorites.filter(pk=user.pk).exists()

    def add_to_favorites(self, user: User):
        self.favorites.add(user)
        self.save()

    def remove_from_favorites(self, user: User):
        self.favorites.remove(user)
        self.save()

    def to_shortcut_item(self):
        """Convert this webapp to a shortcut item dict for GraphQL"""
        return {
            "label": self.name,
            "url": f"/workspaces/{self.workspace.slug}/webapps/{self.slug}/play",
        }

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"<Webapp: {self.name}>"
