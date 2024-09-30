import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hexa.core.models.base import Base
from hexa.user_management.models import User


class MetadataAttribute(Base):
    object_content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
    target = GenericForeignKey("object_content_type", "object_id")

    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True, blank=True)
    system = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["object_content_type", "object_id", "key"],
                name="unique_key_per_data_object",
            )
        ]
        indexes = [
            models.Index(
                fields=["object_content_type", "object_id", "key"],
                name="index_object_key",
            ),
        ]

    def __str__(self):
        return f"<MetadataAttribute key={self.key} object_id={self.object_id} content_type={self.object_content_type}>"


class MetadataMixin:
    """
    Mixin to add metadata functionality to models.
    This mixin allows the model to associate key-value metadata attributes.
    """

    def can_view_metadata(self, user: User):
        raise NotImplementedError

    def can_update_metadata(self, user: User):
        raise NotImplementedError

    def can_delete_metadata(self, user: User):
        raise NotImplementedError

    def add_attribute(self, key, value, system):
        return self.attributes.create(
            key=key,
            value=value,
            system=system,
        )

    def update_attribute(self, key, system, value):
        metadata_attr, _ = self.attributes.update_or_create(
            key=key,
            defaults={
                "value": value,
                "system": system,
            },
        )
        return metadata_attr

    def delete_attribute(self, key):
        return self.attributes.filter(key=key).delete()

    def get_attributes(self, **kwargs):
        return self.attributes.filter(**kwargs).all()
