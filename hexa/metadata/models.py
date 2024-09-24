import base64
import re
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models

from hexa.core.models.base import Base
from hexa.user_management.models import User


class MetadataAttributeManager(models.Manager):
    def get_for_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        return self.filter(content_type=content_type, object_id=instance.pk)


class MetadataAttribute(Base):
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
    data_object = GenericForeignKey("content_type", "object_id")

    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True, blank=True)
    system = models.BooleanField(default=False)
    objects = MetadataAttributeManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "key"],
                name="unique_key_per_data_object",
            )
        ]

    def __str__(self):
        return f"<MetadataAttribute key={self.key} object_id={self.object_id} content_type={self.content_type}>"


class MetadataMixin:
    """
    Mixin to add metadata functionality to models.
    This mixin allows the model to associate key-value metadata attributes.
    """

    @property
    def extended_id(self) -> str:
        app_label = self._meta.app_label
        class_name = self._meta.object_name
        return self.encode_base64_id(str(self.id), f"{app_label}.{class_name}")

    @property
    def class_name(self):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).lower()

    @staticmethod
    def encode_base64_id(id: str, model: str) -> str:
        combined = f"{id}:{model}"
        encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")
        return encoded

    @staticmethod
    def decode_base64_id(encoded_id):
        decoded_bytes = base64.b64decode(encoded_id)
        decoded_str = decoded_bytes.decode("utf-8")
        id, model_type = decoded_str.split(":")
        return id, model_type

    def can_view_metadata(self, user: User):
        permission = f"{self._meta.app_label}.view_{self.class_name}"
        if not user.has_perm(permission, self):
            raise PermissionDenied

    def can_update_metadata(self, user: User):
        permission = f"{self._meta.app_label}.update_{self.class_name}"
        if not user.has_perm(permission, self):
            raise PermissionDenied

    def can_delete_metadata(self, user: User):
        permission = f"{self._meta.app_label}.delete_{self.class_name}"
        if not user.has_perm(permission, self):
            raise PermissionDenied

    def add_attribute(self, key, value, system):
        content_type = ContentType.objects.get_for_model(self)
        created = MetadataAttribute.objects.create(
            content_type=content_type,
            object_id=self.pk,
            key=key,
            value=value,
            system=system,
        )
        return created

    def add_attribute_if_has_permission(self, user, key, value=None, system=False):
        self.can_update_metadata(user)
        return self.add_attribute(key, value, system)

    def update_attribute(self, key, system, value):
        content_type = ContentType.objects.get_for_model(self)
        metadata_attr, created = MetadataAttribute.objects.update_or_create(
            content_type=content_type,
            object_id=self.pk,
            key=key,
            defaults={
                "value": value,
                "system": system,
            },
        )
        return metadata_attr

    def update_attribute_if_has_permission(self, user, key, value=None, system=False):
        self.can_update_metadata(user)
        return self.update_attribute(key, system, value)

    def delete_attribute(self, key):
        content_type = ContentType.objects.get_for_model(self)
        return self.objects.filter(
            content_type=content_type, object_id=self.pk, key=key
        ).delete()

    def delete_attribute_if_has_permission(self, user, key):
        self.can_delete_metadata(user)
        return self.delete_attribute(key)

    def get_attributes(self, **kwargs):
        content_type = ContentType.objects.get_for_model(self)
        metadata_attr = self.objects.filter(
            content_type=content_type,
            object_id=self.pk,
            **kwargs,
        )
        return metadata_attr

    def get_attributes_if_has_permission(
        self, user: User, **kwargs
    ) -> [MetadataAttribute]:
        self.can_view_metadata(user)
        return self.get_attributes(**kwargs).all()
