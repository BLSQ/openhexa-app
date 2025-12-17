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


def create_webapp_slug(name: str, workspace: Workspace):
    """Generate a unique slug for a webapp within a workspace."""
    suffix = ""
    while True:
        slug = slugify(name[: 100 - len(suffix)] + suffix)
        if not Webapp.objects.filter(workspace=workspace, slug=slug).exists():
            return slug
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
        from django.core.exceptions import PermissionDenied

        if not principal.has_perm(
            f"{self.model._meta.app_label}.create_{self.model._meta.model_name}", ws
        ):
            raise PermissionDenied

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

    class WebappType(models.TextChoices):
        IFRAME = "iframe", "iFrame"
        HTML = "html", "HTML"
        BUNDLE = "bundle", "Bundle"
        SUPERSET = "superset", "Superset"

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
    type = models.CharField(
        max_length=20, choices=WebappType.choices, default=WebappType.IFRAME
    )
    is_public = models.BooleanField(default=False)
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
