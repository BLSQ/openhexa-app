from __future__ import annotations

import logging
import typing
import uuid
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import TrigramSimilarity, TrigramWordSimilarity
from django.db import connection, models
from django.db.models import Q, Value
from django.db.models.functions import Greatest
from django.templatetags.static import static
from django_countries.fields import CountryField
from django_ltree.managers import TreeManager, TreeQuerySet

from hexa.core.date_utils import date_format
from hexa.core.models.base import Base, BaseQuerySet
from hexa.core.models.locale import LocaleField
from hexa.core.models.path import PathField
from hexa.core.models.postgres import (
    PostgresTextSearchConfigField,
    locale_to_text_search_config,
)
from hexa.core.search_utils import Token, TokenType, normalize_search_index
from hexa.user_management import models as user_management_models

logger = logging.getLogger(__name__)


class BaseIndexQuerySet(TreeQuerySet, BaseQuerySet):
    def leaves(self, level: int):
        return self.filter(path__depth=level + 1)

    def filter_for_user(self, user: AnonymousUser | user_management_models.User):
        return self._filter_for_user_and_query_object(
            user,
            Q(
                indexpermission__team__in=user_management_models.Team.objects.filter_for_user(
                    user
                )
            ),
        )

    def filter_for_types(self, code_types: list[str]):
        # sub select only those types
        q_predicats = Q()
        for code in code_types:
            try:
                app_code, model_name = code.split("_", 1)
                app_label = f"connector_{app_code}"
                content_type = ContentType.objects.get_by_natural_key(
                    app_label, model_name
                )
            except Exception:
                # invalid code ("_" not in code, app not found, contentType not found)
                continue
            q_predicats |= Q(content_type=content_type)
        query = self.select_related("content_type")
        query = query.filter(q_predicats)
        return query

    def filter_for_tokens(self, tokens: typing.Sequence[Token]):
        trig_query = " ".join([t.value for t in tokens if t.type == TokenType.WORD])
        if trig_query:
            # We mix similarity and word_similarity to achieve better results in long strings
            # See https://dev.to/moritzrieger/build-a-fuzzy-search-with-postgresql-2029
            similarity = Greatest(
                TrigramSimilarity(
                    "search",
                    trig_query,
                ),
                TrigramWordSimilarity(trig_query, "search"),
            )

            # Here, we do 2 things:
            # First, we filter with __trigram_similar, this generates SQL like `WHERE search % 'the query'`
            # where % is the similarity operator (https://www.postgresql.org/docs/current/pgtrgm.html#PGTRGM-OP-TABLE)
            # This operator checks that the similarity is greater than pg_trgm.similarity_threshold
            # We use the operator and not the function as postgresl does not hit the index for the function (sadly)
            # (note: the GIN and GIST indexes are defined directly on the Index model)
            #
            # Then, we annotate with TrigramSimilarity("search", query) and it generates this SQL:
            # `SELECT similarity("search", 'the query') as rank` and this is used to display the rank in the search.
            results = (
                self.filter(
                    Q(search__trigram_similar=trig_query)
                    | Q(search__trigram_word_similar=trig_query)
                )
                # exclude everything called 's3keep', it's noise from s3content manager
                # TODO: don't index these files
                .annotate(rank=similarity)
                .order_by("-rank")
            )

            # pg_trgm.similarity_threshold is by default = 0.3 and this is too low for us.
            # We increase it here.
            # Warning: the SET is done right now but the queryset execution is lazy so could be delayed a lot
            # there is no guarantee that someone will not SET a different value in the meantime
            # (but probability is low)
            with connection.cursor() as cursor:
                cursor.execute("SET pg_trgm.similarity_threshold = %s", [0.1])
        else:
            results = self.annotate(rank=Value(0.5))

        # filter with exact word
        for t in tokens:
            if t.type == TokenType.EXACT_WORD:
                results = results.filter(search__contains=t.value)

        return results


class BaseIndexManager(TreeManager):
    """Only used to override TreeManager.get_queryset(), which prevented us from having our
    own queryset, and re-attach filter_for_user().
    """

    def filter_for_user(self, user: AnonymousUser | user_management_models.User):
        return self.get_queryset().filter_for_user(user)

    def get_queryset(self):  # TODO: PR in django-ltree?
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints)


class BaseIndex(Base):
    """Indexes are entries in the catalog used for search and as anchors for metadata."""

    objects = BaseIndexManager.from_queryset(BaseIndexQuerySet)()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Content-type
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="+"
    )
    object_id = models.UUIDField()
    object = GenericForeignKey("content_type", "object_id")

    # Hierarchy
    path = PathField(
        null=True,
        blank=True,
    )  # TODO: not null, not blank and unique

    # Hexa Metadata
    label = models.TextField(blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        "user_management.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    content = models.TextField(blank=True)
    context = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)
    tags = models.ManyToManyField("tags.Tag", blank=True, related_name="+")
    locale = LocaleField(default="en")
    last_synced_at = models.DateTimeField(null=True, blank=True)

    # External data
    external_id = models.TextField(blank=True)
    external_type = models.TextField(blank=True)
    external_subtype = models.TextField(blank=True)
    external_name = models.TextField(blank=True)
    external_description = models.TextField(blank=True)

    # Search fields / optimizations
    text_search_config = PostgresTextSearchConfigField()
    search = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        """Override to handle Postgres text search config."""
        self.text_search_config = locale_to_text_search_config(self.locale)
        super().save(*args, **kwargs)

    @property
    def app_label(self) -> str:
        return self.content_type.app_label

    @property
    def content_type_name(self) -> str:
        return self.content_type.name

    @property
    def content_type_model(self) -> str:
        return self.content_type.model

    @property
    def display_name(self) -> str:
        return self.label or self.external_name

    @property
    def symbol(self) -> str:
        return static(f"{self.app_label}/img/symbol.svg")

    @classmethod
    def resolve_graphql_type(cls, root, info, result_type):
        if not isinstance(root, cls):
            return None
        return "CatalogEntry"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "object_id": self.object_id,
            "rank": getattr(self, "rank", None),
            "app_label": self.app_label,
            "content_type_model": self.content_type_model,
            "content_type_name": self.content_type_name,
            "display_name": self.display_name,
            "summary": self.content_type_name,
            "symbol": self.symbol,
            "name": self.label,
            "external_name": self.external_name,
            "description": self.description,
            "external_description": self.external_description,
            "countries": [country.code for country in self.countries],
            "last_synced_at": (
                date_format(self.last_synced_at)
                if self.last_synced_at is not None
                else None
            ),
        }

    # TODO: remove me this ugly workaround when we set a value for last_synced_at on all indexes
    def last_synced_at_fallback_to_parent(self):
        last_synced_at = self.last_synced_at
        if self.last_synced_at is None and len(self.path) > 1:
            last_synced_at = self.__class__.objects.get(
                path=self.path[0]
            ).last_synced_at

        return last_synced_at

    def get_absolute_url(self):
        if hasattr(self.object, "get_absolute_url") and callable(
            self.object.get_absolute_url
        ):
            return self.object.get_absolute_url()

        return None


class BaseIndexPermission(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    team = models.ForeignKey(
        "user_management.Team", on_delete=models.CASCADE, related_name="+"
    )

    # Link the the Datasource permission
    permission_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, related_name="+"
    )
    permission_id = models.UUIDField(null=True)
    permission = GenericForeignKey("permission_type", "permission_id")


class BaseIndexableMixin:
    def get_permission_model(self) -> BaseIndexPermission:
        raise NotImplementedError

    def get_index_model(self):
        raise NotImplementedError

    @property
    def index(self):
        # We can't use self.indexes.get(), as it would prevent fetch_related() to work properly
        indexes = getattr(self, "indexes").all()
        if len(indexes) != 1:
            raise ValueError(
                f"{self} should have exactly 1 index - found {len(indexes)}"
            )

        return indexes[0]

    def get_permission_set(self):
        """Return a queryset of permission objects that needs to be indexed.
        (We don't only index content but also their permissions, so that the indexes record can be filtered
        depending on the user permissions).
        """
        raise NotImplementedError

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        getattr(super(), "save")(*args, **kwargs)
        self.build_index()

    def build_index(self):
        IndexModel: models.Model = self.get_index_model()
        try:
            index = IndexModel.objects.get(
                content_type=ContentType.objects.get_for_model(self),
                object_id=getattr(self, "id"),
            )
        except IndexModel.DoesNotExist:
            index = IndexModel(
                content_type=ContentType.objects.get_for_model(self),
                object_id=getattr(self, "id"),
            )

        try:
            self.populate_index(index)
        except NotImplementedError:
            # For some Entry subclasses, we want to skip indexing. This might be an inheritance issue and we
            # might want to refactor this in the future - or make sure that all entries are indexed.
            return

        # Add to the search string the fields from the index (hexa metadata)
        index.search += (
            f" {index.label} {index.description} {index.context} {index.locale}"
        )
        tags = " ".join([x.name for x in index.tags.all()])
        countries = " ".join([f"{x.code} {x.name}" for x in index.countries])
        owner = index.owner.name if index.owner else ""
        index.search += f" {owner} {tags} {countries}"

        # trim duplicate spaces, lower char, remove tab
        index.search = normalize_search_index(index.search)

        index.save()

        self.get_permission_model().objects.filter(index=index.id).delete()
        for permission in self.get_permission_set():
            self.get_permission_model().objects.update_or_create(
                index=index, team=permission.team, defaults={"permission": permission}
            )
