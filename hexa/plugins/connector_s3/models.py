from django.db import models, transaction
from django.template.defaultfilters import pluralize
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
from hexa.core.models.cryptography import EncryptedTextField
from hexa.plugins.connector_s3.api import generate_sts_buckets_credentials


class Credentials(Base):
    """We actually only need one set of credentials. These "principal" credentials will be then used to generate
    short-lived credentials with a tailored policy giving access only to the buckets that the user team can
    access"""

    class Meta:
        verbose_name = "S3 Credentials"
        verbose_name_plural = "S3 Credentials"
        ordering = ("username",)

    username = models.CharField(max_length=200)
    access_key_id = EncryptedTextField()
    secret_access_key = EncryptedTextField()
    role_arn = models.CharField(max_length=200)

    @property
    def display_name(self):
        return self.username

    @property
    def use_sts_credentials(self) -> bool:
        return self.role_arn != ""


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

    s3_name = models.CharField(max_length=200)

    objects = BucketQuerySet.as_manager()

    @property
    def hexa_or_s3_name(self):
        return self.name if self.name != "" else self.s3_name

    def sync(self, user):  # TODO: move in api/sync module
        """Sync the bucket by querying the DHIS2 API"""

        try:
            principal_s3_credentials = Credentials.objects.get()
        except (Credentials.DoesNotExist, Credentials.MultipleObjectsReturned):
            raise ValueError(
                "Your s3 connector plugin should have a single credentials entry"
            )

        sts_credentials = generate_sts_buckets_credentials(
            user=user,
            principal_credentials=principal_s3_credentials,
            buckets=[self],
        )
        fs = S3FileSystem(
            key=sts_credentials["AccessKeyId"],
            secret=sts_credentials["SecretAccessKey"],
            token=sts_credentials["SessionToken"],
        )

        # Sync data elements
        with transaction.atomic():
            # TODO: update or create
            self.object_set.all().delete()
            result = self.create_objects(fs, f"{self.s3_name}")

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
                bucket=self,
                s3_key=object_data["Key"],
                s3_size=object_data["size"],
                s3_storage_class=object_data["StorageClass"],
                s3_type=object_data["type"],
                s3_name=object_data["name"],
                s3_last_modified=object_data.get("LastModified"),
            )

            if s3_object.s3_type == "directory":  # TODO: choices
                results += self.create_objects(fs, s3_object.s3_key)

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
        count = self.object_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d object%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    def index(self):
        catalog_index = CatalogIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.owner,
            name=self.name,
            external_name=self.s3_name,
            countries=self.countries,
            last_synced_at=self.last_synced_at,
            detail_url=reverse("connector_s3:datasource_detail", args=(self.pk,)),
            content_summary=self.content_summary,
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
