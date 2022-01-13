import uuid
from typing import List

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.db import models
from django.db.models import Q
from django.urls import reverse
from dpq.models import BaseJob

from hexa.core.models import BaseIndex, BaseIndexableMixin, BaseIndexPermission
from hexa.core.models.indexes import BaseIndexManager, BaseIndexQuerySet
from hexa.core.search import tokenize


class CatalogIndexQuerySet(BaseIndexQuerySet):
    def search(self, query: str):
        tokens = tokenize(query, ["type", "datasource"])

        # filters
        types = [t.value[5:] for t in tokens if t.value.startswith("type:")]
        datasources = []
        for t in tokens:
            if t.value.startswith("datasource:"):
                try:
                    datasources.append(uuid.UUID(t.value[11:]))
                except ValueError:
                    continue

        # query
        results = (
            self.filter_for_tokens(tokens)
            # filter by resources type
            .filter_for_types(types)
            # filter by datasources
            .filter_for_datasources(datasources)
            # exclude s3keep, artifact of s3content mngt
            .exclude(external_name=".s3keep")
        )

        return results

    def filter_for_datasources(self, ds_ids: List[uuid.UUID]):
        # sub select only those types
        q_predicats = Q()
        for ds_id in ds_ids:
            q_predicats |= Q(datasource_id=ds_id)
        return self.filter(q_predicats)


class Index(BaseIndex):
    # copy container info to help filter search
    datasource_name = models.TextField(blank=True)
    datasource_id = models.UUIDField(null=True)

    objects = BaseIndexManager.from_queryset(CatalogIndexQuerySet)()

    class Meta:
        verbose_name = "Catalog index"
        verbose_name_plural = "Catalog indexes"
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

    def to_dict(self):
        result = super().to_dict()
        result["datasource_name"] = self.datasource_name
        return result


class IndexPermission(BaseIndexPermission):
    index = models.ForeignKey("Index", on_delete=models.CASCADE)


class IndexableMixin(BaseIndexableMixin):
    def get_permission_model(self):
        return IndexPermission

    def get_index_model(self):
        return Index


class CatalogQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        raise NotImplementedError(
            "Catalog querysets should implement the filter_for_user() method"
        )

    def prefetch_indexes(self):
        if not hasattr(self.model, "indexes"):
            raise ValueError(f"Model {self.model} has no indexes")

        return self.prefetch_related("indexes", "indexes__tags")


class Datasource(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auto_sync = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    indexes = GenericRelation("catalog.Index")

    objects = CatalogQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def display_name(self):
        raise NotImplementedError

    def sync(self):
        raise NotImplementedError

    def get_credentials(self):
        raise NotImplementedError

    def sync_url(self):
        return reverse(
            "catalog:datasource_sync",
            kwargs={
                "datasource_id": self.id,
                "datasource_contenttype_id": ContentType.objects.get_for_model(
                    self.__class__
                ).id,
            },
        )


class Entry(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    indexes = GenericRelation("catalog.Index")

    objects = CatalogQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.build_index()


class DatasourcesSyncJob(BaseJob):
    # queue table to hold sync job from django-postgres-queue. Need to redefine this class to specify a
    # custom table name, to avoid conflicts with other queue in the system
    class Meta:
        db_table = "catalog_datasourcessyncjob"
