import base64
import re
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
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


class OpaqueID:
    value: str = None

    def __init__(self, id: uuid.UUID, model: str):
        self.value = self.encode_base64_id(str(id), model)

    @staticmethod
    def encode_base64_id(id: str, model: str) -> str:
        combined = f"{id}:{model}"
        encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")
        return encoded

    @staticmethod
    def decode_base64_id(encoded_id: str) -> (str, str):
        decoded_bytes = base64.b64decode(encoded_id)
        decoded_str = decoded_bytes.decode("utf-8")
        id, model_type = decoded_str.split(":")
        return id, model_type

    def get_decoded_value(self):
        return self.decode_base64_id(self.value)


class MetadataMixin:
    """
    Mixin to add metadata functionality to models.
    This mixin allows the model to associate key-value metadata attributes.
    """

    opaque_id: OpaqueID = None

    class Meta:
        abstract = True

    @property
    def class_name(self):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).lower()

    def _user_has_permission_to(self, user: User, permission: str):
        permission = f"{self._meta.app_label}.{permission}_{self.class_name}"
        if not user.has_perm(permission, self):
            raise PermissionDenied

    def can_view_metadata(self, user: User):
        self._user_has_permission_to(user, "view")

    def can_update_metadata(self, user: User):
        self._user_has_permission_to(user, "update")

    def can_delete_metadata(self, user: User):
        self._user_has_permission_to(user, "delete")

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
