import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class Base(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def display_name(self):
        if hasattr(self, "short_name") and getattr(self, "short_name") != "":
            return self.short_name
        elif hasattr(self, "name") and getattr(self, "name") != "":
            return self.name

        return str(self.id)

    def __str__(self):
        return self.display_name


class Permission(Base):
    class Meta:
        abstract = True

    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)
    index_permission = GenericRelation(
        "catalog.IndexPermission",
        content_type_field="permission_type_id",
        object_id_field="permission_id",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index_object()

    def index_object(self):
        raise NotImplementedError
