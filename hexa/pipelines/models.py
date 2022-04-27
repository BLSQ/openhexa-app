import typing
import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.core.signing import Signer
from django.db import models
from django.http import HttpRequest
from dpq.models import BaseJob

from hexa.core.models import BaseIndex, BaseIndexableMixin, BaseIndexPermission
from hexa.core.models.base import BaseQuerySet


class Index(BaseIndex):
    class Meta:
        verbose_name = "Pipeline index"
        verbose_name_plural = "Pipeline indexes"
        ordering = ("external_name",)
        indexes = [
            GinIndex(
                name="pipeline_index_search_gin_idx",
                fields=["search"],
                opclasses=["gin_trgm_ops"],
            ),
            GistIndex(
                name="pipeline_index_search_gist_idx",
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


class Environment(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    auto_sync = models.BooleanField(default=True)

    indexes = GenericRelation("pipelines.Index")

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True

    def sync(self):
        raise NotImplementedError


class Pipeline(IndexableMixin, models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    indexes = GenericRelation("pipelines.Index")

    objects = BaseQuerySet.as_manager()

    def get_permission_set(self):
        raise NotImplementedError

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def run(
        self,
        *,
        request: HttpRequest,
        conf: typing.Mapping[str, typing.Any] = None,
        webhook_path: str = None,
    ):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.build_index()

    def get_token(self):
        return Signer().sign_object(
            {
                "id": str(self.id),
                "model": self._meta.model_name,
                "app_label": self._meta.app_label,
            }
        )


class EnvironmentsSyncJob(BaseJob):
    # queue table to hold sync job from django-postgres-queue. Need to redefine this class to specify a
    # custom table name, to avoid conflicts with other queue in the system
    class Meta:
        db_table = "catalog_environmentssyncjob"
