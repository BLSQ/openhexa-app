from __future__ import annotations

import uuid

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models

from hexa.user_management import models as user_management_models


class BaseManager(models.Manager):
    def create_if_has_perm(self, principal, **kwargs):
        if not principal.has_perm(
            f"{self.model._meta.app_label}.create_{self.model._meta.model_name}"
        ):
            raise PermissionDenied
        return super().create(**kwargs)

    def update_if_has_perm(self, principal, instance, **kwargs):
        if not principal.has_perm(
            f"{self.model._meta.app_label}.update_{self.model._meta.model_name}",
            instance,
        ):
            raise PermissionDenied
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete_if_has_perm(self, principal, instance):
        if not principal.has_perm(
            f"{self.model._meta.app_label}.delete_{self.model._meta.model_name}",
            instance,
        ):
            raise PermissionDenied
        instance.delete()


class BaseQuerySet(models.QuerySet):
    def filter_for_user(
        self,
        user: (
            AnonymousUser
            | user_management_models.User
            | user_management_models.UserInterface
        ),
    ) -> models.QuerySet:
        """Most catalog / pipelines models need to implement this method for access control."""
        raise NotImplementedError

    def _filter_for_user_and_query_object(
        self,
        user: (
            AnonymousUser
            | user_management_models.User
            | user_management_models.UserInterface
        ),
        query_object: models.Q,
        *,
        return_all_if_superuser: bool = True,
    ) -> models.QuerySet:
        """Helper method useful to keep consistency in access control management within models:

        1. Inactive users (including anonymous users) will get an empty queryset
        2. Superusers will get the full, unfiltered queryset (unless return_all_if_superuser is set to False)
        3. Regular, authenticated users will get the queryset filtered using the query_object argument
        """
        if not user.is_authenticated:
            return self.none()
        elif return_all_if_superuser and user.is_superuser:
            return self.all()

        return self.filter(query_object).distinct()

    def prefetch_indexes(self):
        if not hasattr(self.model, "indexes"):
            raise ValueError(f"Model {self.model} has no indexes")

        return self.prefetch_related("indexes", "indexes__tags")


class Base(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseQuerySet.as_manager()

    @property
    def display_name(self):
        if hasattr(self, "short_name") and getattr(self, "short_name") != "":
            return self.short_name
        elif hasattr(self, "name") and getattr(self, "name") != "":
            return self.name

        return str(self.id)

    def __str__(self):
        return self.display_name
