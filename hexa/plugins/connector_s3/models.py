from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from s3fs import S3FileSystem

from hexa.catalog.models import (
    Base,
    Content,
    Datasource,
    CatalogIndex,
    CatalogIndexPermission,
)
from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.models import Permission


class CredentialsQuerySet(models.QuerySet):
    def get_for_team(self, user):
        # TODO: root credentials concept?
        if user.is_active and user.is_superuser:
            return self.get(team=None)

        if user.team_set.count() == 0:
            raise Credentials.DoesNotExist()

        return self.get(team=user.team_set.first().pk)  # TODO: multiple teams?


class Credentials(Base):
    """This class is a temporary way to store S3 credentials. This approach is not safe for production,
    as credentials are not encrypted.
    TODO: Store credentials in a secure storage engine like Vault.
    """

    class Meta:
        verbose_name = "S3 Credentials"
        verbose_name_plural = "S3 Credentials"
        ordering = ("username",)

    # TODO: unique?
    team = models.ForeignKey(
        "user_management.Team",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="s3_credentials_set",
    )
    username = models.CharField(max_length=200)
    access_key_id = models.CharField(max_length=200)
    secret_access_key = models.CharField(max_length=200)

    objects = CredentialsQuerySet.as_manager()

    @property
    def display_name(self):
        return self.username


class BucketQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            bucketpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Bucket(Datasource):
    class Meta:
        verbose_name = "S3 Bucket"
        ordering = (
            "name",
            "s3_name",
        )

    sync_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )
    s3_name = models.CharField(max_length=200)

    objects = BucketQuerySet.as_manager()

    @property
    def hexa_or_s3_name(self):
        return self.name if self.name != "" else self.s3_name

    def sync(self):  # TODO: move in api/sync module
        """Sync the bucket by querying the DHIS2 API"""

        if self.sync_credentials is True:
            fs = S3FileSystem(anon=True)
        else:
            fs = S3FileSystem(
                key=self.sync_credentials.access_key_id,
                secret=self.sync_credentials.secret_access_key,
            )

        # Sync data elements
        with transaction.atomic():
            # TODO: update or create
            self.object_set.all().delete()
            result = self.create_objects(fs, f"{self.name}")

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return result

    def create_objects(self, fs, path):
        results = DatasourceSyncResult(
            datasource=self,
            created=0,
            updated=0,
            identical=0,
        )

        created = 0
        for object_data in fs.ls(path, detail=True):
            if object_data["Key"][-1] == "/" and object_data["size"] == 0:
                continue  # TODO: check if safer way

            s3_object = Object.objects.create(
                instance=self,
                key=object_data["Key"],
                size=object_data["size"],
                storage_class=object_data["StorageClass"],
                type=object_data["type"],
                s3_name=object_data["name"],
                last_modified=object_data.get("LastModified"),
            )

            if s3_object.type == "directory":  # TODO: choices
                results += self.create_objects(fs, s3_object.key)

            created += 1

        results += DatasourceSyncResult(
            datasource=self,
            created=created,
            updated=0,
            identical=0,
        )

        return results

    @property
    def content_summary(self):
        if self.last_synced_at is None:
            return "Never synced"

        return _("%(object_count)s objects") % {
            "object_count": self.object_set.count(),
        }

    def index(self):
        catalog_index = CatalogIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.owner,
            name=self.name,
            external_name=self.s3_name,
            countries=self.countries,
            last_synced_at=self.last_synced_at,
            detail_url=reverse("connector_s3:datasource_detail", args=(self.pk,)),
        )

        for permission in self.bucketpermission_set.all():
            CatalogIndexPermission.objects.create(
                catalog_index=catalog_index, team=permission.team
            )

    @property
    def display_name(self):
        return self.hexa_or_s3_name


class BucketPermission(Permission):
    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)


class Object(Content):
    class Meta:
        verbose_name = "S3 Object"
        ordering = ["name"]

    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    s3_key = models.TextField()
    s3_size = models.PositiveBigIntegerField()
    s3_storage_class = models.CharField(max_length=200)  # TODO: choices
    s3_type = models.CharField(max_length=200)  # TODO: choices
    s3_name = models.CharField(max_length=200)
    s3_last_modified = models.DateTimeField(null=True)

    @property
    def hexa_or_s3_name(self):
        return self.name if self.name != "" else self.s3_name

    @property
    def display_name(self):
        return self.hexa_or_s3_name
