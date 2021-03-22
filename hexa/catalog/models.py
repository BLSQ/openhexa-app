from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from hexa.common.models import (
    Base,
    PostgresTextSearchConfigField,
    LocaleField,
)
from hexa.common.search import locale_to_text_search_config


class CatalogIndexType(models.TextChoices):
    DATASOURCE = "DATASOURCE", _("Datasource")
    CONTENT = "CONTENT ", _("Content")


class CatalogIndexQuerySet(models.QuerySet):
    def for_user(self, user):
        if not (user.is_active and user.is_superuser):
            return self.none()

        return self

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

        search_vector = SearchVector("name", "description", "countries")
        search_query = SearchQuery(query, config=models.F("text_search_config"))
        search_rank = SearchRank(vector=search_vector, query=search_query)

        results = (
            self.annotate(rank=search_rank).filter(rank__gt=0.01).order_by("-rank")
        )

        if content_type is not None:
            results = results.filter(content_type=content_type)

        results = results[:limit]

        return results

    def create_or_update(self, *, indexed_object, parent_object=None, **kwargs):
        index_type = ContentType.objects.get_for_model(self.model)

        try:
            index = index_type.get_object_for_this_type(object_id=indexed_object.pk)
        except CatalogIndex.DoesNotExist:
            model_type = ContentType.objects.get_for_model(indexed_object)
            if parent_object is not None:
                parent = index_type.get_object_for_this_type(object_id=parent_object.pk)
            else:
                parent = None

            index = CatalogIndex(
                content_type=model_type,
                object_id=indexed_object.pk,
                index_type=indexed_object.index_type,
                parent=parent,
            )

        for name, value in kwargs.items():
            setattr(index, name, value)

        index.save()


class CatalogIndex(Base):
    class Meta:
        verbose_name = "Catalog Index"
        verbose_name_plural = "Catalog indexes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = None

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    object = GenericForeignKey("content_type", "object_id")
    index_type = models.CharField(max_length=100, choices=CatalogIndexType.choices)
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
    def display_name(self):
        return self.short_name if self.short_name is not None else self.name

    @property
    def summary(self):
        summary = self.content_type_name

        if self.parent is not None:
            summary += f" ({self.parent.display_name})"

        return summary

    @property
    def just_synced(self):  # TODO: move (DRY)
        return (
            self.last_synced_at is not None
            and (timezone.now() - self.last_synced_at).seconds < 60
        )

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


class Datasource(Base):
    class Meta:
        abstract = True

    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    url = models.URLField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    active_from = models.DateTimeField(null=True, blank=True)
    active_to = models.DateTimeField(null=True, blank=True)
    public = models.BooleanField(default=False, verbose_name="Public dataset")
    locale = LocaleField(default="en")

    @property
    def index_type(self):
        return CatalogIndexType.DATASOURCE

    @property
    def display_name(self):
        return self.short_name if self.short_name != "" else self.name

    @property
    def just_synced(self):  # TODO: move (DRY)
        return (
            self.last_synced_at is not None
            and (timezone.now() - self.last_synced_at).seconds < 60
        )

    @property
    def content_summary(self):
        raise NotImplementedError(
            "Each datasource model should implement a content_summary property"
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        self.index()

    def index(self):
        """Each datasource model should implement this method to handle indexing in catalog."""

        raise NotImplementedError(
            "Each datasource model subclass should provide a index() method"
        )

    def sync(self):
        raise NotImplementedError(
            "Each datasource model class should implement a sync() method"
        )


class Content(Base):
    class Meta:
        abstract = True

    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=200, blank=True)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    locale = LocaleField(default="en")

    @property
    def index_type(self):
        return CatalogIndexType.CONTENT

    @property
    def just_synced(self):  # TODO: move (DRY)
        return (
            self.last_synced_at is not None
            and (timezone.now() - self.last_synced_at).seconds < 60
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        self.index()

    def index(self):
        """Each concrete content model can override this method to handle indexing in catalog."""

        pass
