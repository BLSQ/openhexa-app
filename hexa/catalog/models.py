from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
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

        search_vector = SearchVector(
            "name",
            "external_name",
            "short_name",
            "external_short_name",
            "description",
            "external_description",
            "countries",
        )
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
            try:
                setattr(index, name, value)
            except AttributeError:
                raise AttributeError(
                    f'Cannot set attribute "{name}" with value "{value}" on {index}'
                )

        index.save()

        return index


class CatalogIndex(Index):
    class Meta:
        verbose_name = "Catalog Index"
        verbose_name_plural = "Catalog indexes"

    index_type = models.CharField(max_length=100, choices=CatalogIndexType.choices)

    objects = CatalogIndexQuerySet.as_manager()


class CatalogIndexPermission(Permission):
    catalog_index = models.ForeignKey("CatalogIndex", on_delete=models.CASCADE)


class Datasource(RichContent, WithIndex, WithSync):
    class Meta:
        abstract = True

    active_from = models.DateTimeField(null=True, blank=True)
    active_to = models.DateTimeField(null=True, blank=True)
    public = models.BooleanField(default=False, verbose_name="Public dataset")

    @property
    def index_type(self):
        return CatalogIndexType.DATASOURCE

    def sync(self):
        raise NotImplementedError("Datasource classes should implement sync()")


class Content(RichContent, WithIndex, WithSync):
    class Meta:
        abstract = True

    @property
    def index_type(self):
        return CatalogIndexType.CONTENT
