from __future__ import annotations

from django.db import models
from django.utils import timezone


class DefaultSoftDeletedManager(models.Manager):
    """
    This manager will return all objects no marked as  soft deleted
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class IncludeSoftDeletedManager(models.Manager):
    """
    A manager that will include all objects (soft_deleted or not)
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

    def delete(self):
        """
        Soft deletes the object.

        """
        self.deleted_at = timezone.now()
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
