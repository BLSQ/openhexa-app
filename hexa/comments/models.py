from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hexa.core.models import Base


class CommentQuerySet(models.QuerySet):
    def for_content(self, content):
        return self.filter(object=content)


class Comment(Base):
    class Meta:
        ordering = ["-created_at"]

    user = models.ForeignKey("user_management.User", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    object = GenericForeignKey("content_type", "object_id")
    text = models.TextField()

    objects = models.Manager.from_queryset(CommentQuerySet)
