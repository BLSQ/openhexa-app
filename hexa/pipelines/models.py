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
            pipelineindexpermission__team__in=[t.pk for t in user.team_set.all()]
        )

    def create_or_update(self, *, indexed_object, parent_object=None, **kwargs):
        index_type = ContentType.objects.get_for_model(self.model)

        try:
            index = index_type.get_object_for_this_type(object_id=indexed_object.pk)
        except PipelinesIndex.DoesNotExist:
            model_type = ContentType.objects.get_for_model(indexed_object)
            if parent_object is not None:
                parent = index_type.get_object_for_this_type(object_id=parent_object.pk)
            else:
                parent = None

            index = PipelinesIndex(
                content_type=model_type,
                object_id=indexed_object.pk,
                index_type=indexed_object.index_type,
                parent=parent,
            )

        for name, value in kwargs.items():
            setattr(index, name, value)

        index.save()

        return index


class PipelinesIndex(Index):
    class Meta:
        verbose_name = "Pipeline Index"
        verbose_name_plural = "Pipeline indexes"

    index_type = models.CharField(max_length=100, choices=PipelinesIndexType.choices)

    objects = PipelinesIndexQuerySet.as_manager()


class PipelinesIndexPermission(Permission):
    pipeline_index = models.ForeignKey("PipelinesIndex", on_delete=models.CASCADE)
