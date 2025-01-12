import typing
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
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
    label = models.CharField(max_length=255, null=True, blank=True)
    value = models.JSONField(default=dict)
    system = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

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
        return f"<MetadataAttribute key={self.key} label={self.label} value={self.value} object_id={self.object_id} content_type={self.object_content_type}>"


class MetadataMixin(models.Model):
    """
    Mixin to add metadata functionality to models.
    This mixin allows the model to associate key-value metadata attributes.
    """

    attributes = GenericRelation(
        MetadataAttribute,
        content_type_field="object_content_type",
        object_id_field="object_id",
    )

    class Meta:
        abstract = True

    def can_view_metadata(self, user: User) -> bool:
        raise NotImplementedError

    def can_update_metadata(self, user: User) -> bool:
        raise NotImplementedError

    def can_delete_metadata(self, user: User) -> bool:
        raise NotImplementedError

    def update_or_create_attribute(
        self,
        key: str,
        value: typing.Any,
        system: bool = False,
        label: str | None = None,
        principal: User | None = None,
    ) -> MetadataAttribute:
        # FIXME: In Django 5 we can use `.update_or_create(key=key, default={}, create_defaults={})` to have the same behaviour but more concise
        try:
            attr = self.attributes.get(key=key)
            attr.value = value
            attr.label = label
            attr.system = system
            attr.updated_by = principal
            attr.save()
            return attr
        except MetadataAttribute.DoesNotExist:
            return self.attributes.create(
                created_by=principal,
                updated_by=principal,
                key=key,
                value=value,
                label=label,
                system=system,
            )

    def delete_attribute(self, key: str) -> None:
        attr: MetadataAttribute = self.attributes.get(key=key)
        attr.delete()
