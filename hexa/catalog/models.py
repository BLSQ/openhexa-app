import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.contrib.postgres.search import (
    TrigramSimilarity,
)
from django.db import models, connection
from django_countries.fields import CountryField
from django_ltree.managers import TreeQuerySet, TreeManager

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
from hexa.core.models.path import PathField
from hexa.core.models.postgres import locale_to_text_search_config


class IndexQuerySet(TreeQuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            indexpermission__team__in=[t.pk for t in user.team_set.all()]
        )

    def search(self, query):
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

        sim = TrigramSimilarity("search", query)

        results = (
            self.filter(search__trigram_similar=query)
            .annotate(rank=sim)
            .order_by("-rank")
        )

        if content_type is not None:
            results = results.filter(content_type=content_type)

        with connection.cursor() as cursor:
            cursor.execute("SET pg_trgm.similarity_threshold = %s", [0.1])

        return results.select_related("content_type")


class IndexManager(TreeManager):
    """Only used to override TreeManager.get_queryset(), which prevented us from having our
    own queryset."""

    def get_queryset(self):  # TODO: PR in django-ltree?
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints)


class Index(Base):
    class Meta:
        verbose_name = "Catalog Index"
        verbose_name_plural = "Catalog indexes"
        ordering = ("external_name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = None

    class Meta:
        indexes = [
            GinIndex(
                name="catalog_index_search_gin_idx",
                fields=["search"],
                opclasses=["gin_trgm_ops"],
            ),
            GistIndex(
                name="catalog_index_search_gist_idx",
                fields=["search"],
                opclasses=["gist_trgm_ops"],
            ),
        ]

    # Content-type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    object = GenericForeignKey("content_type", "object_id")

    # Hierarchy
    path = PathField(
        null=True,
        blank=True,
    )  # TODO: not null, not blank and unique

    # Hexa Metadata
    label = models.TextField(blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    content = models.TextField(blank=True)
    context = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    tags = models.ManyToManyField("tags.Tag", blank=True)
    locale = LocaleField(default="en")
    last_synced_at = models.DateTimeField(null=True, blank=True)
    # TODO: add comments

    # External data
    external_id = models.TextField(blank=True)
    external_type = models.TextField(blank=True)
    external_subtype = models.TextField(blank=True)
    external_name = models.TextField(blank=True)
    external_description = models.TextField(blank=True)

    # Search fields / optimizations
    text_search_config = PostgresTextSearchConfigField()
    search = models.TextField(blank=True)

    objects = IndexManager.from_queryset(IndexQuerySet)()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """Override save() to handle Postgres text search config."""

        self.text_search_config = locale_to_text_search_config(self.locale)
        super().save(force_insert, force_update, using, update_fields)

    @property
    def app_label(self):  # TODO: check
        return self.content_type.app_label

    @property
    def content_type_name(self):  # TODO: check
        return self.content_type.name

    @property
    def display_name(self):
        return self.label or self.external_name

    @property
    def symbol(self):  # TODO: check
        return f"{settings.STATIC_URL}{self.app_label}/img/symbol.svg"

    def to_dict(self):
        return {  # TODO: adapt to new models
            "id": self.id,
            # "parent": self.parent.to_dict() if self.parent is not None else None,
            "rank": self.rank,
            "app_label": self.app_label,
            "content_type_name": self.content_type_name,
            "display_name": self.display_name,
            # "summary": self.summary,
            "symbol": self.symbol,
            # "name": self.name,
            "external_name": self.external_name,
            # "short_name": self.short_name,
            # "external_short_name": self.external_short_name,
            "description": self.description,
            "external_description": self.external_description,
            "countries": [country.code for country in self.countries],
            # "detail_url": self.detail_url,
            "last_synced_at": date_format(self.last_synced_at)
            if self.last_synced_at is not None
            else None,
        }


class IndexPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)
    index = models.ForeignKey("Index", on_delete=models.CASCADE)


class Datasource(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    indexes = GenericRelation("catalog.Index")

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

    def sync(self):
        raise NotImplementedError(
            "Datasource models should implement the sync() method"
        )


class Entry(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    indexes = GenericRelation("catalog.Index")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    def index(self):
        raise NotImplementedError(
            "Datasource models should implement the index() method"
        )
