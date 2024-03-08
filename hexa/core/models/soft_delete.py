from __future__ import annotations

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        for obj in self.all():
            obj.delete()

    def hard_delete(self):
        super().delete()


class DefaultSoftDeletedManager(models.Manager):
    """
    This manager will return all objects not marked as  soft deleted
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class IncludeSoftDeletedManager(models.Manager):
    """
    A manager that returns all objects (soft_deleted or not)
    """

    def get_queryset(self):
        return super().get_queryset()


class SoftDeletedOnlyManager(models.Manager):
    """
    A manager that handles soft deleted objects (deleted_at is not null).
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeletedModel(models.Model):
    """
    A Django model which has been enhanced with soft deletion characteristics.

    """

    class Meta:
        abstract = True

    deleted_at = models.DateTimeField(default=None, blank=True, null=True)
    restored_at = models.DateTimeField(default=None, blank=True, null=True)

    objects = DefaultSoftDeletedManager()
    all_objects = IncludeSoftDeletedManager()
    deleted_objects = SoftDeletedOnlyManager()

    @property
    def is_deleted(self):
        """
        Check if the object has been deleted.

        """
        return self.deleted_at is not None

    @property
    def is_restored(self):
        """
        Checks if the object has been restored.

        """
        return self.restored_at is not None

    def delete(self):
        """
        Soft deletes the object.

        """
        self.deleted_at = timezone.now()
        self.restored_at = None
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """
        Deletes the object from the database permanently.
        """
        return super().delete(using, keep_parents)

    def restore(self):
        """
        Restores a soft deleted object.
        """
        self.deleted_at = None
        self.restored_at = timezone.now()

        self.save()
