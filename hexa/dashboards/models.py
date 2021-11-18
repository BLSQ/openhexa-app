import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.db import models

from hexa.core.models import (
    BaseIndex,
    BaseIndexableMixin,
    BaseIndexPermission,
    Permission,
)


class Index(BaseIndex):
    class Meta:
        verbose_name = "Dashboard index"
        verbose_name_plural = "Dashboard indexes"
        ordering = ("external_name",)
        indexes = [
            GinIndex(
                name="dashboard_index_search_gin_idx",
                fields=["search"],
                opclasses=["gin_trgm_ops"],
            ),
            GistIndex(
                name="dashboard_index_search_gist_idx",
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


class DashboardsQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        return self

    def prefetch_indexes(self):
        return self.prefetch_related("indexes", "indexes__tags")


class ExternalDashboard(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.URLField()
    picture = models.FileField(upload_to="external_dashboard")

    indexes = GenericRelation("dashboards.Index")

    objects = DashboardsQuerySet.as_manager()

    def populate_index(self, index):
        index.content = self.url
        index.path = [self.id.hex]
        index.search = f"{self.url}"

    def get_permission_set(self):
        return self.externaldashboardpermission_set.all()

    def __str__(self):
        return f"ExternalDashboard for '{self.url}'"

    def get_absolute_url(self):
        return ""


class ExternalDashboardPermission(Permission):
    external_dashboard = models.ForeignKey(ExternalDashboard, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("external_dashboard", "team")]

    def index_object(self):
        self.external_dashboard.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on dashboard '{self.dashboard}'"
