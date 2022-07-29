from __future__ import annotations

import typing

from django.contrib.auth.models import AnonymousUser
from django.db import models, transaction
from django_countries.fields import Country, CountryField
from model_utils.managers import InheritanceManager, InheritanceQuerySet

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.tags.models import Tag
from hexa.user_management import models as user_management_models
from hexa.user_management.models import User, UserInterface


class CollectionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: UserInterface):
        return self.all()


class CollectionManager(models.Manager):
    @transaction.atomic
    def create_if_has_perm(
        self,
        principal: UserInterface,
        *,
        name: str,
        author: User = None,
        countries: typing.Sequence[Country] = None,  # TODO: use hexa.countries ?
        tags: typing.Sequence[Tag] = None,
        description: str = "",
    ):
        # TODO: check if has perm & create owner permissions

        collection = self.create(
            name=name, author=author, countries=countries, description=description
        )
        if tags is not None:
            collection.tags.set(tags)

        return collection


class Collection(Base):
    name = models.TextField()
    author = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    countries = CountryField(multiple=True, blank=True)
    tags = models.ManyToManyField("tags.Tag", blank=True, related_name="+")
    description = models.TextField(blank=True)

    objects = CollectionManager.from_queryset(CollectionQuerySet)()

    def delete_if_has_perm(
        self,
        principal: UserInterface,
    ):
        # TODO: check if has perm

        self.delete()


class CollectionItemQuerySet(BaseQuerySet, InheritanceQuerySet):
    def filter_for_user(
        self,
        user: typing.Union[
            AnonymousUser,
            user_management_models.User,
            user_management_models.UserInterface,
        ],
    ) -> models.QuerySet:
        # TODO: implement filter

        return self.all()


class CollectionItemManager(InheritanceManager):
    """Unfortunately, InheritanceManager does not support from_queryset, so we have to subclass it
    and "re-attach" the queryset methods ourselves."""

    def get_queryset(self):
        return CollectionItemQuerySet(self.model)

    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.get_queryset().filter_for_user(user)


class CollectionItem(Base):
    # TODO: cannot add unique constraint on "collection" + "field in subclass"
    # TODO: Consider validating uniqueness in model method

    class Meta:
        ordering = ["-created_at"]

    item: models.ForeignKey = None
    collection = models.ForeignKey(
        "data_collections.Collection", on_delete=models.CASCADE, related_name="+"
    )

    objects = CollectionItemManager()

    @property
    def graphql_item_type(self):
        raise NotImplementedError
