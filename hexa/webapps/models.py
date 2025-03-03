from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models import Q

from hexa.core.models.base import Base, BaseManager, BaseQuerySet
from hexa.core.models.soft_delete import (
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class WebappManager(BaseManager):
    pass


class WebappQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            Q(workspace__members=user),
            return_all_if_superuser=False,
        )


class Webapp(Base, SoftDeletedModel):
    class Meta:
        verbose_name = "Webapp"
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "name",
                name="unique_webapp_name_per_workspace",
                condition=Q(deleted_at__isnull=True),
            )
        ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.BinaryField(blank=True, null=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="webapps"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    favorites = models.ManyToManyField(
        User, related_name="favorite_webapps", blank=True
    )
    objects = WebappManager.from_queryset(WebappQuerySet)()

    def add_to_favorites(self, user: User):
        self.favorites.add(user)
        self.save()

    def remove_from_favorites(self, user: User):
        self.favorites.remove(user)
        self.save()

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"<Webapp: {self.name}>"
