import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from hexa.core.models import RichContent, WithIndex, Index, Permission


class Environment(RichContent, WithIndex):
    class Meta:
        abstract = True

    @property
    def index_type(self):
        return PipelinesIndexType.PIPELINES_ENVIRONMENT


class Pipeline(RichContent):
    class Meta:
        abstract = True

    @property
    def index_type(self):
        return PipelinesIndexType.PIPELINES_PIPELINE


class PipelinesIndexType(models.TextChoices):
    PIPELINES_ENVIRONMENT = "PIPELINES_ENVIRONMENT", _("Pipeline environment")
    PIPELINES_PIPELINE = "PIPELINES_PIPELINE", _("Pipeline")


class PipelinesIndexQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            pipelinesindexpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class PipelinesIndex(Index):
    class Meta:
        verbose_name = "Pipeline Index"
        verbose_name_plural = "Pipeline indexes"

    index_type = models.CharField(max_length=100, choices=PipelinesIndexType.choices)

    objects = PipelinesIndexQuerySet.as_manager()


class PipelinesIndexPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)
    pipeline_index = models.ForeignKey("PipelinesIndex", on_delete=models.CASCADE)
