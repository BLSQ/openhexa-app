from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.formats import date_format
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
import uuid

from hexa.common.models import Base, LocaleField, PostgresTextSearchConfigField
from hexa.common.search import locale_to_text_search_config


class PipelineEnvironment(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hexa_owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    hexa_name = models.CharField(max_length=200, blank=True)
    hexa_short_name = models.CharField(max_length=100, blank=True)
    hexa_description = models.TextField(blank=True)
    hexa_countries = CountryField(multiple=True, blank=True)
    hexa_last_synced_at = models.DateTimeField(null=True, blank=True)
    hexa_active_from = models.DateTimeField(null=True, blank=True)
    hexa_active_to = models.DateTimeField(null=True, blank=True)
    hexa_created_at = models.DateTimeField(auto_now_add=True)
    hexa_updated_at = models.DateTimeField(auto_now=True)

    @property
    def index_type(self):
        return PipelineIndexType.PIPELINE_SERVER

    @property
    def display_name(self):
        return self.hexa_short_name if self.hexa_short_name != "" else self.hexa_name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        self.index()

    def index(self):
        """Each pipeline server model should implement this method to handle indexing in the pipelines."""

        raise NotImplementedError(
            "Each pipeline server model subclass should provide a index() method"
        )


class PipelineIndexType(models.TextChoices):
    PIPELINE_SERVER = "PIPELINE_SERVER", _("Pipeline Server")


class PipelineIndexQuerySet(models.QuerySet):
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
        except PipelineIndex.DoesNotExist:
            model_type = ContentType.objects.get_for_model(indexed_object)
            if parent_object is not None:
                parent = index_type.get_object_for_this_type(object_id=parent_object.pk)
            else:
                parent = None

            index = PipelineIndex(
                content_type=model_type,
                object_id=indexed_object.pk,
                index_type=indexed_object.index_type,
                parent=parent,
            )

        for name, value in kwargs.items():
            setattr(index, name, value)

        index.save()

        return index


class PipelineIndex(Base):
    class Meta:
        verbose_name = "Pipeline Index"
        verbose_name_plural = "Pipeline indexes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = None

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    object = GenericForeignKey("content_type", "object_id")
    index_type = models.CharField(max_length=100, choices=PipelineIndexType.choices)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    detail_url = models.URLField()
    content_summary = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    locale = LocaleField(default="en")
    text_search_config = PostgresTextSearchConfigField()

    objects = PipelineIndexQuerySet.as_manager()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """Override save() to handle Postgres text search config."""

        self.text_search_config = locale_to_text_search_config(self.locale)
        super().save(force_insert, force_update, using, update_fields)

    @property
    def app_label(self):
        return self.content_type.app_label

    @property
    def content_type_name(self):
        return self.content_type.name

    @property
    def display_name(self):
        return self.short_name if self.short_name is not None else self.name

    @property
    def summary(self):
        summary = self.content_type_name

        if self.parent is not None:
            summary += f" ({self.parent.display_name})"

        return summary

    @property
    def symbol(self):
        return f"{settings.STATIC_URL}{self.app_label}/img/symbol.svg"

    def to_dict(self):  # TODO: use serializer
        return {
            "id": self.id,
            "parent": self.parent.to_dict() if self.parent is not None else None,
            "rank": self.rank,
            "app_label": self.app_label,
            "content_type_name": self.content_type_name,
            "display_name": self.display_name,
            "summary": self.summary,
            "symbol": self.symbol,
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "countries": [country.code for country in self.countries],
            "detail_url": self.detail_url,
            "last_synced_at": date_format(self.last_synced_at, "M d, H:i:s (e)")
            if self.last_synced_at is not None
            else None,
        }


class PipelineIndexPermission(Base):
    pipeline_index = models.ForeignKey("PipelineIndex", on_delete=models.CASCADE)
    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)
