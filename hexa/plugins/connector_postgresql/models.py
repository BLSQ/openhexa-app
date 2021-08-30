import json
import uuid
from enum import Enum

import psycopg2
from django.contrib.contenttypes.fields import GenericRelation

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from hexa.catalog.models import (
    Index,
    IndexPermission,
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


class Database(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_synced_at = models.DateTimeField(null=True, blank=True)

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    def index(self):
        index, _ = Index.objects.update_or_create(
            defaults={
                "external_name": self.database,
                "external_id": self.safe_url,
                "external_type": ExternalType.DATABASE.value,
                "search": f"{self.database}",
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )

        for permission in self.databasepermission_set.all():
            IndexPermission.objects.get_or_create(index=index, team=permission.team)

    @property
    def display_name(self):
        return self.unique_name

    def __str__(self):
        return self.display_name

    def sync(self, user):
        with psycopg2.connect(self.url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """
                )
                response = cursor.fetchall()

        created_count = 0
        updated_count = 0
        identical_count = 0
        new_orphans_count = 0

        with transaction.atomic():
            tables = {x[0] for x in response}
            existing_tables = Table.objects.filter(database=self)
            for table in existing_tables:
                if table.name not in tables:
                    new_orphans_count += 1
                    table.delete()
                else:
                    table.save()
                    identical_count += 1
            for new_table in tables - {x.name for x in existing_tables}:
                created_count += 1
                Table.objects.create(name=new_table, database=self)

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


class TableQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            database__databasepermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    database = models.ForeignKey("Database", on_delete=models.CASCADE)
    name = models.CharField(max_length=512)
    indexes = GenericRelation("catalog.Index")

    class Meta:
        verbose_name = "PostgreSQL table"
        ordering = ["name"]

    objects = TableQuerySet.as_manager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    def index(self):
        index, _ = Index.objects.update_or_create(
            defaults={
                "last_synced_at": self.database.last_synced_at,
                "external_name": self.name,
                "external_type": ExternalType.TABLE.value,
                "path": f"{self.database.pk}.{self.pk}".replace("-", ""),
                "external_id": f"{self.database.safe_url}/{self.name}",
                "context": self.database.database,
                "search": f"{self.name}",
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )

        for permission in self.database.databasepermission_set.all():
            IndexPermission.objects.get_or_create(index=index, team=permission.team)


class DatabasePermission(Permission):
    database = models.ForeignKey(
        "connector_postgresql.Database", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [("database", "team")]

    def index_object(self):
        self.database.index()

    def __str__(self):
        return f"Permission for team '{self.team}' on database '{self.database}'"
