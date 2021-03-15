from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from habari.common.models import (
    Base,
    PostgresTextSearchConfigField,
    LocaleField,
)
from habari.common.search import locale_to_text_search_config


class CatalogIndexType(models.TextChoices):
    DATASOURCE = "DATASOURCE", _("Datasource")
    CONTENT = "CONTENT ", _("Content")


class CatalogIndexQuerySet(models.QuerySet):
    def search(self, query, *, content_type=None, limit=10):
        search_vector = SearchVector("name", "description", "countries")
        search_query = SearchQuery(query, config=models.F("text_search_config"))
        search_rank = SearchRank(vector=search_vector, query=search_query)

        results = (
            self.annotate(rank=search_rank)
            .filter(rank__gt=0.01)
            .order_by("-rank")[:limit]
        )

        if content_type is not None:
            results = results.filter(content_type=content_type)

        return results

    def get_or_create_for_content(self, model, *, parent_model=None):
        index_type = ContentType.objects.get_for_model(self.model)

        try:
            return index_type.get_object_for_this_type(object_id=model.pk)
        except CatalogIndex.DoesNotExist:
            model_type = ContentType.objects.get_for_model(model)
            if parent_model is not None:
                parent = index_type.get_object_for_this_type(object_id=parent_model.pk)
            else:
                parent = None

            return CatalogIndex(
                content_type=model_type,
                object_id=model.pk,
                index_type=model.index_type,
                parent=parent,
            )


class CatalogIndex(Base):
    class Meta:
        verbose_name = "Catalog Index"
        verbose_name_plural = "Catalog indexes"

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
    url = models.URLField(blank=True)
    content_summary = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    locale = LocaleField(default="en")
    text_search_config = PostgresTextSearchConfigField()

    objects = CatalogIndexQuerySet.as_manager()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.text_search_config = locale_to_text_search_config(self.locale)
        super().save(force_insert, force_update, using, update_fields)

    @property
    def app_label(self):
        return self.content_type.app_label

    @property
    def model_name(self):
        return self.content_type.name

    def to_dict(self):  # TODO: use serializer
        return {
            "id": self.id,
            "app_label": self.content_type.app_label,
            "model_name": self.content_type.model,
            "object_id": self.object_id,
            "index_type": self.index_type,
            "parent": self.parent.pk if self.parent is not None else None,
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "countries": [country.code for country in self.countries],
            "url": self.url,
            "last_synced_at": self.last_synced_at.isoformat()
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
    def content_summary(self):
        raise NotImplementedError(
            "Each datasource model should implement a content_summary property"
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        index = CatalogIndex.objects.get_or_create_for_content(self)
        self.populate_index(index)
        index.save()

    def populate_index(self, index):
        """Each datasource model can override this method to fine-tune indexing in catalog."""

        index.owner = self.owner
        index.name = self.name
        index.short_name = self.short_name
        index.description = self.description
        index.countries = self.countries
        index.url = self.url
        index.content_summary = self.content_summary

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
    def datasource(self):
        raise NotImplementedError(
            "Each content model subclass should provide a datasource() property that proxies the foreign key "
            "to the content datasource."
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        index = CatalogIndex.objects.get_or_create_for_content(
            self, parent_model=self.datasource
        )
        self.populate_index(index)
        index.save()

    def populate_index(self, index):
        """Each concrete content model should override this method to handle indexing in catalog."""

        pass
