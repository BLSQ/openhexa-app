from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hexa.core.models.base import Base, BaseManager, BaseQuerySet
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class ShortcutQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        # Shortcuts are personal/user-specific by design. Unlike other resources
        # where superusers have broad access, shortcuts should always be filtered
        # to the requesting user only (even for superusers).
        return self._filter_for_user_and_query_object(
            user,
            models.Q(user=user),
            return_all_if_superuser=False,
        )

    def filter_for_workspace(self, workspace: Workspace):
        return self.filter(workspace=workspace)

    def filter_by_content_type(self, model_class: type):
        content_type = ContentType.objects.get_for_model(model_class)
        return self.filter(content_type=content_type)

    def filter_by_content_types(self, *model_classes: type):
        """Filter shortcuts by multiple content types."""
        content_types = [
            ContentType.objects.get_for_model(model_class)
            for model_class in model_classes
        ]
        return self.filter(content_type__in=content_types)


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

    def to_shortcut_item(self):
        """
        Convert this shortcut to a shortcut item dict for GraphQL.
        Returns None if the content object doesn't exist or doesn't implement to_shortcut_item.
        """
        content_object = self.content_object
        if content_object is None:
            return None

        # Skip soft-deleted objects
        if (
            hasattr(content_object, "deleted_at")
            and content_object.deleted_at is not None
        ):
            return None

        if not hasattr(content_object, "to_shortcut_item"):
            return None

        item_data = content_object.to_shortcut_item()
        if item_data is None:
            return None

        return {
            "id": str(content_object.id),
            "name": item_data.get("label", ""),
            "url": item_data.get("url", ""),
            "order": self.order,
        }
