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
        description: str = None,
    ):
        # TODO: check if has perm & create owner permissions

        create_kwargs = {"name": name, "author": author}
        if countries is not None:
            create_kwargs["countries"] = countries
        if description is not None:
            create_kwargs["description"] = description

        collection = self.create(**create_kwargs)
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


class CollectionElementQuerySet(BaseQuerySet, InheritanceQuerySet):
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


class CollectionElementManager(InheritanceManager):
    """Unfortunately, InheritanceManager does not support from_queryset, so we have to subclass it
    and "re-attach" the queryset methods ourselves."""

    def get_queryset(self):
        return CollectionElementQuerySet(self.model)

    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.get_queryset().filter_for_user(user)


class CollectionElement(Base):
    # TODO: cannot add unique constraint on "collection" + "field in subclass"
    # TODO: Consider validating uniqueness in model method

    class Meta:
        ordering = ["-created_at"]

    element: models.ForeignKey = None
    collection = models.ForeignKey(
        "data_collections.Collection", on_delete=models.CASCADE, related_name="+"
    )

    objects = CollectionElementManager()

    @property
    def graphql_element_type(self):
        raise NotImplementedError
