import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)
from django.db import models
from django.db.models.functions import Greatest
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from hexa.core.date_utils import date_format
from hexa.core.models import (
    Base,
    Permission,
    RichContent,
    WithIndex,
    WithSync,
    LocaleField,
    PostgresTextSearchConfigField,
)
from hexa.core.models.postgres import locale_to_text_search_config


class CatalogIndexType(models.TextChoices):
    # TODO: prefix with CATALOG
    DATASOURCE = "DATASOURCE", _("Datasource")
    CONTENT = "CONTENT ", _("Content")


class CatalogIndexQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            catalogindexpermission__team__in=[t.pk for t in user.team_set.all()]
        )

    def search(self, query, *, limit=10):
        tokens = query.split(" ")

        try:
            content_type_code = next(t for t in tokens if t[:5] == "type:")[5:]
            other_tokens = [t for t in tokens if t[:5] != "type:"]
            query = " ".join(other_tokens)
            app_code, model_name = content_type_code.split("_", 1)
            app_label = f"connector_{app_code}"
            content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
        except StopIteration:
            content_type = None

        # We want the text search to lookup all those fields
        fields = [
            "name",
            "external_name",
            "short_name",
            "external_short_name",
            "description",
            "external_description",
            "countries",
        ]

        # We use SearchVector to instruct the SearchQuery
        # to look in all those fields
        search_vector = SearchVector(*fields)
        search_query = SearchQuery(query, config=models.F("text_search_config"))
        search_rank = SearchRank(vector=search_vector, query=search_query)

        # Unfortunately, using `SearchQuery` works nicely only when the user
        # types a full word (or better, multiple words).
        # But if you type only part of a word `SearchQuery` will not return a match
        # This is particularly annoying for S3 objects as their "name" is
        # considered as single word (slashes don't count as spaces)
        # So we also match on trigrams for all fields and take the field
        # that has the highest match and combine it with the match from the SearchVector
        trigrams = [TrigramSimilarity(field, query) for field in fields]
        max_trigram = Greatest(*trigrams)

        results = (
            self.annotate(rank=search_rank + max_trigram)
            .filter(rank__gt=0.11)
            .order_by("-rank")
        )

        if content_type is not None:
            results = results.filter(content_type=content_type)

        if limit is not None:
            results = results[:limit]

        return results


class CatalogIndex(Base):
    class Meta:
        verbose_name = "Catalog Index"
        verbose_name_plural = "Catalog indexes"
        ordering = ("name",)

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
    index_type = models.CharField(max_length=100, choices=CatalogIndexType.choices)

    objects = CatalogIndexQuerySet.as_manager()

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


class CatalogIndexPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)
    catalog_index = models.ForeignKey("CatalogIndex", on_delete=models.CASCADE)


class Datasource(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    indexes = GenericRelation("catalog.CatalogIndex")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    @property
    def display_name(self):
        raise NotImplementedError(
            "Datasource models should implement the display_name() property"
        )

    def index(self):
        raise NotImplementedError(
            "Datasource models should implement the index() method"
        )

    def sync(self, user):
        raise NotImplementedError(
            "Datasource models should implement the sync() method"
        )


class Entry(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    indexes = GenericRelation("catalog.CatalogIndex")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    def index(self):
        raise NotImplementedError(
            "Datasource models should implement the index() method"
        )
