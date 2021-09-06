from abc import ABC

import uuid

from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.contrib.postgres.search import (
    TrigramSimilarity,
    TrigramBase,
)
from django.db import models, connection
from django.db.models import Field, Q
from django.db.models.functions import Greatest
from django.db.models.lookups import PostgresOperatorLookup
from django.templatetags.static import static
from django_countries.fields import CountryField
from django_ltree.managers import TreeQuerySet, TreeManager

from hexa.core.date_utils import date_format
from hexa.core.models import (
    Base,
    Permission,
    RichContent,
    LocaleField,
    PostgresTextSearchConfigField,
)
from hexa.core.models.path import PathField
from hexa.core.models.postgres import locale_to_text_search_config


# Those "advanced" lookups and functions are not yet in Django (3.2)
# We implement them here for now. Hopefully there will be redundant
# in the next version
@Field.register_lookup
class TrigramWordSimilar(PostgresOperatorLookup):
    lookup_name = "trigram_word_similar"
    postgres_operator = "%%>"


class TrigramWordSimilarity(TrigramBase):
    function = "WORD_SIMILARITY"


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

        # We mix similarity and word_similarity to achieve better results in long strings
        # See https://dev.to/moritzrieger/build-a-fuzzy-search-with-postgresql-2029
        similarity = Greatest(
            TrigramSimilarity("search", query), TrigramWordSimilarity("search", query)
        )

        # Here, we do 2 things:
        # First, we filter with __trigram_similar, this generates SQL like `WHERE search % 'the query'`
        # where % is the similarity operator (https://www.postgresql.org/docs/current/pgtrgm.html#PGTRGM-OP-TABLE)
        # This operator checks that the similarity is greater than pg_trgm.similarity_threshold
        # We use the operator and not the function as postgresl does not hit the index for the function (sadly)
        # (note: the GIN and GIST indexes are defined directly on the Index model)
        #
        # Then, we annotate with TrigramSimilarity("search", query) and it generates this SQL:
        # `SELECT similarity("search", 'the query') as rank` and this is used to display the rank in the search.
        results = (
            self.filter(
                Q(search__trigram_similar=query) | Q(search__trigram_word_similar=query)
            )
            .annotate(rank=similarity)
            .order_by("-rank")
        )

        if content_type is not None:
            results = results.filter(content_type=content_type)

        # pg_trgm.similarity_threshold is by default = 0.3 and this is too low for us.
        # We increase it here.
        # Warning: the SET is done right now but the queryset execution is lazy so could be delayed a lot
        # there is no guarantee that someone will not SET a different value in the meantime. (but probability is low)
        with connection.cursor() as cursor:
            cursor.execute("SET pg_trgm.similarity_threshold = %s", [0.1])

        return results.select_related("content_type")


class IndexManager(TreeManager):
    """Only used to override TreeManager.get_queryset(), which prevented us from having our
    own queryset."""

    def get_queryset(self):  # TODO: PR in django-ltree?
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints)


class Index(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rank = None

    class Meta:
        verbose_name = "Index"
        verbose_name_plural = "Indexes"
        ordering = ("external_name",)
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
        return static(f"{self.app_label}/img/symbol.svg")

    def to_dict(self):
        return {  # TODO: adapt to new models
            "id": self.id,
            "rank": self.rank,
            "app_label": self.app_label,
            "content_type_name": self.content_type_name,
            "display_name": self.display_name,
            "summary": self.content_type_name,
            "symbol": self.symbol,
            "name": self.label,
            "external_name": self.external_name,
            "description": self.description,
            "external_description": self.external_description,
            "countries": [country.code for country in self.countries],
            "url": self.object.get_absolute_url(),
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


class WithIndex:
    def get_permission_set(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    def index(self):
        index, _ = Index.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )
        self.update_index(index)
        index.save()

        for permission in self.get_permission_set():
            IndexPermission.objects.get_or_create(index=index, team=permission.team)

    def update_index(self, index):
        raise NotImplementedError(
            "Each indexable model should implement the make_index() method"
        )


class Datasource(models.Model, WithIndex):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    indexes = GenericRelation("catalog.Index")

    @property
    def display_name(self):
        raise NotImplementedError(
            "Datasource models should implement the display_name() property"
        )

    def sync(self):
        raise NotImplementedError(
            "Datasource models should implement the sync() method"
        )

    @property
    def only_index(self):  # TODO: discuss, ugly but index() already exist
        return self.indexes.get()


class Entry(models.Model, WithIndex):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    indexes = GenericRelation("catalog.Index")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    @property
    def only_index(self):  # TODO: discuss, ugly but index() already exist
        return self.indexes.get()
