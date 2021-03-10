from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from functools import lru_cache

from django_countries.fields import CountryField

from habari.catalog.connectors import (
    get_connector_app_configs,
)
from habari.common.models import (
    Base,
    DynamicTextChoices,
    PostgresTextSearchConfigField,
    LocaleField,
)


class CatalogModel(Base):
    class Meta:
        abstract = True

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    @property
    def display_name(self):
        return self.short_name if self.short_name != "" else self.name

    @property
    def just_synced(self):
        return (
            self.last_synced_at is not None
            and (timezone.now() - self.last_synced_at).seconds < 60
        )

    def __str__(self):
        return self.display_name


class DatasourceType(DynamicTextChoices):
    @staticmethod
    @lru_cache
    def build_choices():
        choices = {}
        for app in get_connector_app_configs():
            if app.datasource_type is not None:
                choices[app.datasource_type] = (
                    app.datasource_type,
                    _(app.datasource_type),
                )

        return choices


class DatasourceItem(CatalogModel):
    """Contains the fields shared by the concrete data source models in the different connectors and the index model"""

    class Meta:
        abstract = True

    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    datasource_type = models.CharField(choices=DatasourceType.choices, max_length=100)
    url = models.URLField(blank=True)
    active_from = models.DateTimeField(null=True, blank=True)
    active_to = models.DateTimeField(null=True, blank=True)
    public = models.BooleanField(default=False, verbose_name="Public dataset")


class DatasourceIndexQuerySet(models.QuerySet):
    def search(self, query, *, limit=10, search_type=None):
        if search_type is not None and search_type != "datasource":
            return []

        search_vector = SearchVector("name", "short_name", "description", "countries")
        search_query = SearchQuery(query)
        search_rank = SearchRank(vector=search_vector, query=search_query)

        return (
            self.annotate(rank=search_rank).filter(rank__gt=0).order_by("-rank")[:limit]
        )


class DatasourceIndex(DatasourceItem):
    """A datasource index is an searchable, browsable datasource entry. It does not contain any platform-specific
    information - each connector will provide concrete datasource models for that purpose."""

    text_search_config = PostgresTextSearchConfigField()
    objects = DatasourceIndexQuerySet.as_manager()


class Datasource(DatasourceItem):
    class Meta:
        abstract = True

    datasource_index = models.ForeignKey(
        "catalog.DatasourceIndex",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    preferred_locale = LocaleField(default="en")

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)

        index = (
            DatasourceIndex()
            if self.datasource_index is None
            else self.datasource_index
        )
        self.update_index(index)

    def update_index(self, index):
        """Each concrete datasource model can implement this method to populate the catalog index."""

        pass


class ContentItem(CatalogModel):
    """Contains the fields shared by the concrete content models in the different connectors and the index model"""

    class Meta:
        abstract = True


class ContentIndexQuerySet(models.QuerySet):
    def search(self, query, *, limit=10, search_type=None):
        if search_type is not None and search_type != "dhis2_data_element":
            return []

        search_vector = SearchVector(
            "external_id",
            "dhis2_name",
            "dhis2_short_name",
            "dhis2_description",
            config=models.F("datasource__text_search_config"),
        )
        search_query = SearchQuery(
            query, config=models.F("datasource__text_search_config")
        )
        search_rank = SearchRank(vector=search_vector, query=search_query)

        return (
            self.annotate(rank=search_rank).filter(rank__gt=0).order_by("-rank")[:limit]
        )


class ContentIndex(ContentItem):
    """A content index is a searchable, browsable piece of content accessible in a datasource. Just like
    datasource indexes, it does not contain any platform-specific information and each connector will have to
     provide concrete content models."""

    datasource_index = models.ForeignKey(
        "DatasourceIndex",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    objects = ContentIndexQuerySet.as_manager()


class Content(ContentItem):
    class Meta:
        abstract = True

    content_index = models.ForeignKey(
        "catalog.ContentIndex",
        on_delete=models.CASCADE,
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)

        # Create or update index
        if self.content_index is None:
            self.content_index = ContentIndex.objects.create()
        else:
            self.content_index.bar = "baz"
            self.content_index.save()
