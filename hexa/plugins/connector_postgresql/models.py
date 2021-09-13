import json
import uuid
from enum import Enum

import psycopg2
from django.contrib.contenttypes.fields import GenericRelation

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from psycopg2 import OperationalError
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import (
    Index,
    IndexPermission,
    Datasource,
    Entry,
)
from hexa.catalog.sync import DatasourceSyncResult

from hexa.core.models import Permission
from hexa.core.models.cryptography import EncryptedTextField


class ExternalType(Enum):
    DATABASE = "database"
    TABLE = "table"


class DatabaseQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            databasepermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Database(Datasource):
    def get_permission_set(self):
        return self.databasepermission_set.all()

    hostname = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = EncryptedTextField(max_length=200)
    port = models.IntegerField(default=5432)
    database = models.CharField(max_length=200)

    postfix = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Postgresql Database"
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
    def env_name(self):
        slug = self.unique_name.replace("-", "_").upper()
        return f"POSTGRESQL_{slug}"

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

    def sync(self):
        with psycopg2.connect(self.url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name, table_type, pg_class.reltuples
                    FROM information_schema.tables
                    JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """
                )
                response = cursor.fetchall()

        created_count = 0
        updated_count = 0
        identical_count = 0
        new_orphans_count = 0

        # Ignore tables from postgis as there is no value in showing them in the catalog
        IGNORE_TABLES = ["geography_columns", "geometry_columns", "spatial_ref_sys"]

        with transaction.atomic():
            new_tables = {x[0]: x for x in response if x[0] not in IGNORE_TABLES}
            existing_tables = Table.objects.filter(database=self)
            for table in existing_tables:
                if table.name not in new_tables.keys():
                    new_orphans_count += 1
                    table.delete()
                else:
                    data = new_tables[table.name]
                    if table.rows == data[2]:
                        identical_count += 1
                    else:
                        table.rows = data[2]
                        updated_count += 1
                    table.save()

            for new_table_name, new_table in new_tables.items():
                if new_table_name not in {x.name for x in existing_tables}:
                    created_count += 1
                    Table.objects.create(
                        name=new_table_name, database=self, rows=new_table[2]
                    )

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return DatasourceSyncResult(
            datasource=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            orphaned=new_orphans_count,
        )

    def get_absolute_url(self):
        return reverse(
            "connector_postgresql:datasource_detail", kwargs={"datasource_id": self.id}
        )


class TableQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            database__databasepermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Table(Entry):
    def get_permission_set(self):
        return self.database.databasepermission_set.all()

    database = models.ForeignKey("Database", on_delete=models.CASCADE)
    name = models.CharField(max_length=512)
    rows = models.IntegerField(default=0)

    class Meta:
        verbose_name = "PostgreSQL table"
        ordering = ["name"]

    objects = TableQuerySet.as_manager()

    def populate_index(self, index):
        index.last_synced_at = self.database.last_synced_at
        index.external_name = self.name
        index.external_type = ExternalType.TABLE.value
        index.path = [self.database.id.hex, self.id.hex]
        index.external_id = f"{self.database.safe_url}/{self.name}"
        index.context = self.database.database
        index.search = f"{self.name}"

    def get_absolute_url(self):
        return reverse(
            "connector_postgresql:table_detail",
            kwargs={"datasource_id": self.database.id, "table_id": self.id},
        )


class DatabasePermission(Permission):
    database = models.ForeignKey(
        "connector_postgresql.Database", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [("database", "team")]

    def index_object(self):
        self.database.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on database '{self.database}'"
