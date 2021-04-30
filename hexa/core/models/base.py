import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_countries.fields import CountryField

from hexa.core.date_utils import date_format
from hexa.core.models.locale import LocaleField
from hexa.core.models.postgres import (
    PostgresTextSearchConfigField,
    locale_to_text_search_config,
)


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


class RichContent(Base):
    class Meta:
        abstract = True

    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    comments = GenericRelation("comments.Comment")
    name = models.CharField(max_length=200, blank=True)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    locale = LocaleField(default="en")

    @property
    def content_summary(self):
        return ""


class Index(Base):
    class Meta:
        verbose_name = "Pipeline Index"
        verbose_name_plural = "Pipeline indexes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = None

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    object = GenericForeignKey("content_type", "object_id")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=200)
    external_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    external_short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    external_description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    locale = LocaleField(default="en")
    detail_url = models.URLField()
    content_summary = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    text_search_config = PostgresTextSearchConfigField()

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
        return f"{settings.STATIC_URL}{self.app_label}/img/symbol.svg"

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
