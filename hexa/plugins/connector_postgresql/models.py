import typing
from enum import Enum
from logging import getLogger

import psycopg2
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from psycopg2 import OperationalError

from hexa.catalog.models import Datasource, Entry
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.cryptography import EncryptedTextField
from hexa.user_management.models import Permission, Team, User

logger = getLogger(__name__)


class ExternalType(Enum):
    DATABASE = "database"
    TABLE = "table"


class DatabaseQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(databasepermission__team__in=Team.objects.filter_for_user(user)),
        )


class Database(Datasource):
    def get_permission_set(self):
        return self.databasepermission_set.all()

    searchable = True  # TODO: remove (see comment in datasource_index command)

    hostname = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = EncryptedTextField(max_length=200)
    port = models.IntegerField(default=5432)
    database = models.CharField(max_length=200)

    postfix = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "PostgreSQL Database"
        ordering = ("hostname",)
        unique_together = [("database", "postfix")]

    objects = DatabaseQuerySet.as_manager()

    @property
    def unique_name(self):
        if self.postfix:
            return f"{self.database}{self.postfix}"
        else:
            return self.database

    @property
    def url(self):
        return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"

    @property
    def safe_url(self):
        return (
            f"postgresql://{self.username}@{self.hostname}:{self.port}/{self.database}"
        )

    @property
    def content_summary(self):
        count = self.table_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d table%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    def populate_index(self, index):
        index.last_synced_at = self.last_synced_at
        index.external_name = self.database
        index.external_id = self.safe_url
        index.external_type = ExternalType.DATABASE.value
        index.search = f"{self.database}"
        index.path = [self.id.hex]
        index.content = self.content_summary
        index.datasource_name = self.database
        index.datasource_id = self.id

    def index_all_objects(self):
        logger.info("index_all_objects %s", self.id)
        for table in self.table_set.all():
            try:
                with transaction.atomic():
                    table.build_index()
            except Exception:
                logger.exception("index error")

    @property
    def display_name(self):
        return self.unique_name

    def __str__(self):
        return self.display_name

    def clean(self):
        try:
            with psycopg2.connect(self.url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 = 1")
                    cursor.fetchall()
        except OperationalError as e:
            if "could not connect to server" in str(e):
                raise ValidationError(
                    "Could not connect to server, please check hostname and port"
                )
            elif str(e).startswith("FATAL: "):
                err = str(e).removeprefix("FATAL: ")
                raise ValidationError(err)
            else:
                raise ValidationError(e)

    def get_absolute_url(self):
        return reverse(
            "connector_postgresql:datasource_detail", kwargs={"datasource_id": self.id}
        )


class TableQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(database__in=Database.objects.filter_for_user(user))


class Table(Entry):
    database = models.ForeignKey("Database", on_delete=models.CASCADE)
    name = models.CharField(max_length=512)
    rows = models.IntegerField(default=0)

    searchable = True  # TODO: remove (see comment in datasource_index command)

    class Meta:
        verbose_name = "PostgreSQL table"
        ordering = ["name"]

    objects = TableQuerySet.as_manager()

    def get_permission_set(self):
        return self.database.databasepermission_set.all()

    def populate_index(self, index):
        index.last_synced_at = self.database.last_synced_at
        index.external_name = self.name
        index.external_type = ExternalType.TABLE.value
        index.path = [self.database.id.hex, self.id.hex]
        index.external_id = f"{self.database.safe_url}/{self.name}"
        index.context = self.database.database
        index.search = f"{self.name}"
        index.datasource_name = self.database.database
        index.datasource_id = self.database.id

    def get_absolute_url(self):
        return reverse(
            "connector_postgresql:table_detail",
            kwargs={"datasource_id": self.database.id, "table_id": self.id},
        )


class DatabasePermission(Permission):
    class Meta(Permission.Meta):
        constraints = [
            models.UniqueConstraint(
                "team",
                "database",
                name="database_unique_team",
                condition=Q(team__isnull=False),
            ),
            models.UniqueConstraint(
                "user",
                "database",
                name="database_unique_user",
                condition=Q(user__isnull=False),
            ),
            models.CheckConstraint(
                check=Q(team__isnull=False) | Q(user__isnull=False),
                name="database_permission_user_or_team_not_null",
            ),
        ]

    database = models.ForeignKey(
        "connector_postgresql.Database", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Permission for team '{self.team}' on database '{self.database}'"
