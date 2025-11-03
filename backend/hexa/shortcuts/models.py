from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hexa.core.models.base import Base, BaseManager, BaseQuerySet
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class ShortcutQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            models.Q(user=user),
            return_all_if_superuser=False,
        )

    def filter_for_workspace(self, workspace: Workspace):
        return self.filter(workspace=workspace)

    def filter_by_content_type(self, model_class):
        content_type = ContentType.objects.get_for_model(model_class)
        return self.filter(content_type=content_type)


class ShortcutManager(BaseManager.from_queryset(ShortcutQuerySet)):
    pass


class Shortcut(Base):
    """User-specific, workspace-scoped shortcuts using ContentType framework."""

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

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    order = models.IntegerField(default=0)

    objects = ShortcutManager()

    def __str__(self):
        return f"{self.user.email} - {self.content_object} (workspace: {self.workspace.slug})"

    def __repr__(self):
        return f"<Shortcut: user={self.user.email} content={self.content_object} workspace={self.workspace.slug}>"
