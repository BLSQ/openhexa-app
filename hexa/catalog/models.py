import uuid
from django.contrib.contenttypes.fields import GenericRelation

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.db import models

from hexa.core.models import (
    Base,
    Permission,
    RichContent,
)
from hexa.core.models import (
    BaseIndex,
    BaseIndexPermission,
    BaseIndexableMixin,
)


class Index(BaseIndex):
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


class IndexPermission(BaseIndexPermission):
    index = models.ForeignKey("Index", on_delete=models.CASCADE)


class IndexableMixin(BaseIndexableMixin):
    def get_permission_model(self):
        return IndexPermission

    def get_index_model(self):
        return Index


class DatasourceQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        raise NotImplementedError(
            "Datasource QuerySet should implement the filter_for_user() method"
        )


class Datasource(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    indexes = GenericRelation("catalog.Index")

    objects = DatasourceQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def display_name(self):
        raise NotImplementedError(
            "Datasource models should implement the display_name() property"
        )

    def sync(self):
        raise NotImplementedError(
            "Datasource models should implement the sync() method"
        )


class Entry(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    indexes = GenericRelation("catalog.Index")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.build_index()
