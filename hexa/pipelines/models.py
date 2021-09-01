import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from hexa.core.date_utils import date_format
from hexa.core.models import (
    RichContent,
    WithIndex,
    Permission,
    LocaleField,
    PostgresTextSearchConfigField,
    Base,
)
from hexa.core.models.postgres import locale_to_text_search_config


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


class PipelinesIndex(Base):
    class Meta:
        verbose_name = "Pipeline Index"
        verbose_name_plural = "Pipeline indexes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = None

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    object = GenericForeignKey("content_type", "object_id")
    # TODO: remove?
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    # TODO: remove?
    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.TextField(blank=True)
    external_name = models.TextField(blank=True)
    short_name = models.CharField(max_length=200, blank=True)
    external_short_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    external_description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    locale = LocaleField(default="en")
    detail_url = models.TextField()
    content_summary = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    text_search_config = PostgresTextSearchConfigField()
    index_type = models.CharField(max_length=100, choices=PipelinesIndexType.choices)

    objects = PipelinesIndexQuerySet.as_manager()

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
    def name_or_external_name(self):
        return self.name if self.name != "" else self.external_name

    @property
    def short_name_or_external_short_name(self):
        return self.short_name if self.short_name != "" else self.external_short_name

    @property
    def display_name(self):
        return (
            self.short_name_or_external_short_name
            if self.short_name_or_external_short_name != ""
            else self.name_or_external_name
        )

    @property
    def summary(self):
        summary = self.content_type_name

        if self.parent is not None:
            summary += f" ({self.parent.display_name})"

        return summary

    @property
    def symbol(self):
        return static(f"{self.app_label}/img/symbol.svg")

    def to_dict(self):
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
            "external_name": self.external_name,
            "short_name": self.short_name,
            "external_short_name": self.external_short_name,
            "description": self.description,
            "external_description": self.external_description,
            "countries": [country.code for country in self.countries],
            "detail_url": self.detail_url,
            "last_synced_at": date_format(self.last_synced_at)
            if self.last_synced_at is not None
            else None,
        }


class PipelinesIndexPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)
    pipeline_index = models.ForeignKey("PipelinesIndex", on_delete=models.CASCADE)
