from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property

from hexa.core.models.base import Base, BaseManager, BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


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
    pass


class AllWebappManager(
    BaseManager, IncludeSoftDeletedManager.from_queryset(WebappQuerySet)
):
    pass


class Webapp(Base, SoftDeletedModel):
    class Meta:
        verbose_name = "Webapp"
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "name",
                name="unique_webapp_name_per_workspace",
                condition=Q(deleted_at__isnull=True),
            )
        ]

    name = models.CharField(max_length=255)
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

    @cached_property
    def _shortcut_content_type(self):
        """Cache the ContentType for this model to avoid repeated lookups"""
        return ContentType.objects.get_for_model(self.__class__)

    def is_shortcut(self, user: User):
        """Check if this webapp is a shortcut for the user"""
        from hexa.shortcuts.models import Shortcut

        return Shortcut.objects.filter(
            user=user, content_type=self._shortcut_content_type, object_id=self.id
        ).exists()

    def add_to_shortcuts(self, user: User):
        """Add this webapp to user's shortcuts"""
        from hexa.shortcuts.models import Shortcut

        Shortcut.objects.get_or_create(
            user=user,
            content_type=self._shortcut_content_type,
            object_id=self.id,
            defaults={"workspace": self.workspace},
        )

    def remove_from_shortcuts(self, user: User):
        """Remove this webapp from user's shortcuts"""
        from hexa.shortcuts.models import Shortcut

        Shortcut.objects.filter(
            user=user, content_type=self._shortcut_content_type, object_id=self.id
        ).delete()

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"<Webapp: {self.name}>"
