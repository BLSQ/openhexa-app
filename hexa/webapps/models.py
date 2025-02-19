from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q

from hexa.core.models.base import Base, BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class WebappManager(DefaultSoftDeletedManager):
    def create_if_has_perm(self, principal: User, *args, **kwargs):
        if not principal.has_perm("webapps.create_webapp"):
            raise PermissionDenied

        return super().create_if_has_perm(principal, *args, **kwargs)


class WebappQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            Q(workspace__members=user),
            return_all_if_superuser=False,
        )


class Webapp(Base, SoftDeletedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="webapps"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    objects = WebappManager.from_queryset(WebappQuerySet)()

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"<Webapp: {self.name}>"
