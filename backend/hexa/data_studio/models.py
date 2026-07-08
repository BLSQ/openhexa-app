from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models

from hexa.core.models.base import Base, BaseQuerySet
from hexa.user_management.models import User, UserInterface
from hexa.workspaces.models import Workspace


class SavedQueryQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        return self.filter(workspace__in=Workspace.objects.filter_for_user(user))


class SavedQueryManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: Workspace,
        *,
        name: str,
        content: str,
        description: str = "",
    ):
        if not principal.has_perm("data_studio.create_saved_query", workspace):
            raise PermissionDenied

        return self.create(
            workspace=workspace,
            created_by=principal,
            name=name,
            content=content,
            description=description,
        )


class SavedQuery(Base):
    """A SQL query saved by a user in the Data Studio, shared with the whole workspace."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="saved_queries",
    )
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True, default="")
    content = models.TextField()

    objects = SavedQueryManager.from_queryset(SavedQueryQuerySet)()

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.name

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("data_studio.update_saved_query", self):
            raise PermissionDenied

        for key in ["name", "description", "content"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        return self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("data_studio.delete_saved_query", self):
            raise PermissionDenied

        return self.delete()
