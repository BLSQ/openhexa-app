from abc import abstractmethod

from django.contrib.contenttypes.models import ContentType

from hexa.user_management.models import User


class ShortcutableMixin:
    """
    Mixin for models that can be added to user shortcuts.

    Models using this mixin must:
    1. Have an 'id' field (UUID)
    2. Have a 'workspace' field (ForeignKey to Workspace)
    3. Implement the abstract 'to_shortcut_item()' method
    """

    def is_shortcut(self, user: User) -> bool:
        """Check if this item is a shortcut for the user."""
        from hexa.shortcuts.models import Shortcut

        content_type = ContentType.objects.get_for_model(self.__class__)
        return Shortcut.objects.filter(
            user=user, content_type=content_type, object_id=self.id
        ).exists()

    def add_to_shortcuts(self, user: User) -> None:
        """Add this item to user's shortcuts."""
        from hexa.shortcuts.models import Shortcut

        content_type = ContentType.objects.get_for_model(self.__class__)
        Shortcut.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=self.id,
            defaults={"workspace": self.workspace},
        )

    def remove_from_shortcuts(self, user: User) -> None:
        """Remove this item from user's shortcuts."""
        from hexa.shortcuts.models import Shortcut

        content_type = ContentType.objects.get_for_model(self.__class__)
        Shortcut.objects.filter(
            user=user, content_type=content_type, object_id=self.id
        ).delete()

    @abstractmethod
    def to_shortcut_item(self, shortcut):
        """
        Convert this item to a shortcut item dict for GraphQL.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement to_shortcut_item()"
        )
