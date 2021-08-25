import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from hexa.core.models import (
    Base,
    Index,
    Permission,
    RichContent,
    WithIndex,
    WithSync,
)
from django.db.models.functions import Greatest


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


class CatalogIndex(Index):
    class Meta:
        verbose_name = "Catalog Index"
        verbose_name_plural = "Catalog indexes"
        ordering = ("name",)

    index_type = models.CharField(max_length=100, choices=CatalogIndexType.choices)

    objects = CatalogIndexQuerySet.as_manager()


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
