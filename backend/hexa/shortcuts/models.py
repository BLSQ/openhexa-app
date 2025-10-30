from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hexa.core.models.base import Base, BaseManager, BaseQuerySet
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class ShortcutQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        """Filter shortcuts for a specific user"""
        return self._filter_for_user_and_query_object(
            user,
            models.Q(user=user),
            return_all_if_superuser=False,
        )

    def filter_for_workspace(self, workspace: Workspace):
        """Filter shortcuts for a specific workspace"""
        return self.filter(workspace=workspace)

    def filter_by_content_type(self, model_class):
        """Filter shortcuts by content type (e.g., Webapp, Pipeline)"""
        content_type = ContentType.objects.get_for_model(model_class)
        return self.filter(content_type=content_type)


class ShortcutManager(BaseManager.from_queryset(ShortcutQuerySet)):
    pass


class Shortcut(Base):
    """
    Generic shortcut model that can reference any content type.

    This model uses Django's ContentType framework to create shortcuts
    to any model in the system (webapps, pipelines, datasets, etc.).

    Shortcuts are:
    - User-specific: Each user has their own shortcuts
    - Workspace-scoped: Shortcuts are created within a workspace context
    - Ordered: Users can customize the order of their shortcuts
    - Extensible: Can be applied to any model without schema changes
    """

    class Meta:
        verbose_name = "Shortcut"
        verbose_name_plural = "Shortcuts"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "workspace", "content_type", "object_id"],
                name="unique_user_workspace_content_shortcut",
            )
        ]
        ordering = ["order", "-created_at"]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shortcuts")
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="shortcuts"
    )

    # Generic foreign key to allow shortcuts for any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Optional custom ordering (lower numbers appear first)
    order = models.IntegerField(default=0)

    objects = ShortcutManager()

    def __str__(self):
        return f"{self.user.email} - {self.content_object} (workspace: {self.workspace.slug})"

    def __repr__(self):
        return f"<Shortcut: user={self.user.email} content={self.content_object} workspace={self.workspace.slug}>"
