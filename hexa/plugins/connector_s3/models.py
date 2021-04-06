from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from s3fs import S3FileSystem

from hexa.catalog.models import Base, Content, Datasource, CatalogIndex
from hexa.catalog.sync import DatasourceSyncResult


class CredentialsQuerySet(models.QuerySet):
    def get_for_user(self, user):
        if not (user.is_active and user.is_superuser):
            raise Credentials.DoesNotExist()

        return self.get(user=user)


class Credentials(Base):
    """This class is a temporary way to store S3 credentials. This approach is not safe for production,
    as credentials are not encrypted.
    TODO: Store credentials in a secure storage engine like Vault.
    """

    class Meta:
        verbose_name = "S3 Credentials"
        verbose_name_plural = "S3 Credentials"
        ordering = ("username",)

    # TODO: always link to a user?
    # TODO: unique?
    user = models.ForeignKey(
        "user_management.User", null=True, blank=True, on_delete=models.CASCADE
    )
    username = models.CharField(max_length=200)
    access_key_id = models.CharField(max_length=200)
    secret_access_key = models.CharField(max_length=200)

    objects = CredentialsQuerySet.as_manager()

    def __str__(self):
        return self.username


class BucketQuerySet(models.QuerySet):
    def for_user(self, user):
        if not (user.is_active and user.is_superuser):
            return self.none()

        return self


class Bucket(Datasource):
    class Meta:
        verbose_name = "S3 Bucket"
        ordering = ("hexa_name",)

    name = models.CharField(max_length=200)
    sync_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )

    objects = BucketQuerySet.as_manager()

    def sync(self):
        """Sync the bucket by querying the DHIS2 API"""

        if self.credentials is True:
            fs = S3FileSystem(anon=True)
        else:
            fs = S3FileSystem(
                key=self.credentials.access_key_id,
                secret=self.credentials.secret_access_key,
            )

        # Sync data elements
        with transaction.atomic():
            # TODO: update or create
            Bucket.objects.all().delete()
            result = self.create_objects(fs, f"{self.name}")

            # Flag the datasource as synced
            self.hexa_last_synced_at = timezone.now()
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
                name=object_data["name"],
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
        if self.hexa_last_synced_at is None:
            return ""

        return _("%(object_count)s objects") % {
            "object_count": self.object_set.count(),
        }

    def index(self):
        CatalogIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.hexa_owner,
            name=self.name,
            countries=self.hexa_countries,
            content_summary=self.content_summary,  # TODO: why?
            last_synced_at=self.hexa_last_synced_at,
            detail_url=reverse("connector_s3:datasource_detail", args=(self.pk,)),
        )


class Object(Content):
    class Meta:
        verbose_name = "S3 Object"
        ordering = ["name"]

    instance = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    key = models.TextField()
    size = models.PositiveIntegerField()
    storage_class = models.CharField(max_length=200)  # TODO: choices
    type = models.CharField(max_length=200)  # TODO: choices
    name = models.CharField(max_length=200)
    last_modified = models.DateTimeField(null=True)

    @property
    def display_name(self):
        return self.name

    def index(self):
        pass  # TODO: implement
