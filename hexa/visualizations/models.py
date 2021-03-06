import typing
import uuid

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.db import models
from django.db.models import Q

from hexa.core.models import BaseIndex, BaseIndexableMixin, BaseIndexPermission
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.cryptography import EncryptedTextField
from hexa.user_management.models import Permission, Team, User


class Index(BaseIndex):
    class Meta:
        verbose_name = "Dashboard index"
        verbose_name_plural = "Dashboard indexes"
        ordering = ("label",)
        indexes = [
            GinIndex(
                name="ext_dashboard_index_gin_idx",
                fields=["search"],
                opclasses=["gin_trgm_ops"],
            ),
            GistIndex(
                name="ext_dashboard_index_gist_idx",
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


class ExternalDashboardsQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(externaldashboardpermission__team__in=Team.objects.filter_for_user(user)),
        )

    def prefetch_indexes(self):
        return self.prefetch_related("indexes", "indexes__tags")


class ExternalDashboard(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.URLField()
    picture = models.FileField(upload_to="external_dashboard")
    credentials = EncryptedTextField(null=True, blank=True)

    indexes = GenericRelation("visualizations.Index")

    objects = ExternalDashboardsQuerySet.as_manager()

    def populate_index(self, index):
        index.external_name = "Untitled Dashboard"  # TODO: Name field?
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
    class Meta(Permission.Meta):
        constraints = [
            models.UniqueConstraint(
                "team",
                "external_dashboard",
                name="dashboard_unique_team",
                condition=Q(team__isnull=False),
            ),
            models.UniqueConstraint(
                "user",
                "external_dashboard",
                name="dashboard_unique_user",
                condition=Q(user__isnull=False),
            ),
            models.CheckConstraint(
                check=Q(team__isnull=False) | Q(user__isnull=False),
                name="dashboard_permission_user_or_team_not_null",
            ),
        ]

    external_dashboard = models.ForeignKey(ExternalDashboard, on_delete=models.CASCADE)

    def index_object(self):
        self.external_dashboard.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on dashboard '{self.external_dashboard}'"
