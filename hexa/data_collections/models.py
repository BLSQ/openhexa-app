from __future__ import annotations

import typing
from functools import cache

import django.apps
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import TrigramSimilarity, TrigramWordSimilarity
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models import Q, Value
from django.db.models.functions import Greatest
from django.templatetags.static import static
from django_countries.fields import Country, CountryField
from model_utils.managers import InheritanceManager, InheritanceQuerySet

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.core.search_utils import TokenType, tokenize
from hexa.tags.models import Tag
from hexa.user_management import models as user_management_models
from hexa.user_management.models import User, UserInterface


class CollectionQuerySet(BaseQuerySet):
    def search(self, query: str, min_rank=0.3):
        qs = self

        tokens = tokenize(query)
        trigram_query = " ".join([t.value for t in tokens if t.type == TokenType.WORD])
        if trigram_query:
            similarity = Greatest(
                TrigramSimilarity("name", query)
                + TrigramSimilarity("description", query),
                TrigramWordSimilarity(query, "name")
                + TrigramWordSimilarity(query, "description"),
            )
            qs = qs.filter(
                Q(name__trigram_similar=trigram_query)
                | Q(name__trigram_word_similar=trigram_query)
                | Q(description__trigram_similar=trigram_query)
                | Q(description__trigram_word_similar=trigram_query)
            )
            qs = qs.annotate(rank=similarity)
        else:
            qs = qs.annotate(rank=Value(0.5))

        # filter with exact word
        for t in tokens:
            if t.type == TokenType.EXACT_WORD:
                qs = qs.filter(
                    Q(name__contains=t.value) | Q(description__contains=t.value)
                )

        return qs.filter(rank__gte=min_rank).order_by("-rank")

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
        summary: str = None,
    ):
        if not principal.has_perm("data_collections.create_collection"):
            raise PermissionDenied

        create_kwargs = {"name": name, "author": author}
        if countries is not None:
            create_kwargs["countries"] = countries
        if description is not None:
            create_kwargs["description"] = description
        if summary is not None:
            create_kwargs["summary"] = summary

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
    summary = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)

    objects = CollectionManager.from_queryset(CollectionQuerySet)()

    def delete_if_has_perm(
        self,
        principal: UserInterface,
    ):
        if not principal.has_perm("data_collections.delete_collection", self):
            raise PermissionDenied

        self.delete()

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("data_collections.update_collection", self):
            raise PermissionDenied

        for key in ["name", "description", "summary"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        if kwargs.get("countries", None) is not None:
            self.countries = [c for c in kwargs["countries"] if c is not None]

        if kwargs.get("tags", None) is not None:
            self.tags = [tag for tag in kwargs["tags"] if tag is not None]

        return self.save()

    def add_object(self, principal: UserInterface, object: models.Model):
        return CollectionElement.objects.create_if_has_perm(
            principal, collection=self, object=object
        )

    def get_absolute_url(self) -> str:
        return f"/collections/{self.id}"

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": static("data_collections/img/collection.svg"),
            "rank": getattr(self, "rank", None),
            "app_label": "data_collections",
            "content_type_name": "Collection",
            "display_name": self.name,
            "url": self.get_absolute_url(),
            "countries": [country.code for country in self.countries],
        }


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

    def filter_for_object(self, object: models.Model):
        object_type = ContentType.objects.get_for_model(object)
        return self.filter(object_type=object_type, object_id=object.id)


class CollectionElementManager(InheritanceManager):
    """Unfortunately, InheritanceManager does not support from_queryset, so we have to subclass it
    and "re-attach" the queryset methods ourselves."""

    def get_queryset(self):
        return CollectionElementQuerySet(self.model)

    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.get_queryset().filter_for_user(user)

    def create_if_has_perm(
        self,
        principal: User,
        collection: Collection,
        object: models.Model,
        **kwargs,
    ):
        if not principal.has_perm(
            "data_collections.create_collection_element", collection
        ):
            raise PermissionDenied

        return self.create(
            collection=collection,
            object=object,
            **kwargs,
        )


@cache
def limit_data_source_types():
    from hexa.core.models.indexes import BaseIndexableMixin

    all_models = django.apps.apps.get_models()
    indexables = [x for x in all_models if issubclass(x, BaseIndexableMixin)]
    names = [x.__name__.lower() for x in indexables]
    return {"model__in": names}


class CollectionElement(Base):
    # TODO: cannot add unique constraint on "collection" + "field in subclass"
    # TODO: Consider validating uniqueness in model method

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "collection_id",
                "object_type",
                "object_id",
                name="collection_element_unique_object",
            )
        ]

    collection = models.ForeignKey(
        "data_collections.Collection", on_delete=models.CASCADE, related_name="elements"
    )
    object_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        limit_choices_to=limit_data_source_types,
    )
    object_id = models.UUIDField(null=True)
    object = GenericForeignKey("object_type", "object_id")

    objects = CollectionElementManager()

    def delete_if_has_perm(
        self,
        principal: UserInterface,
    ):
        if not principal.has_perm("data_collections.delete_collection_element", self):
            raise PermissionDenied

        self.delete()
