import json

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from s3fs import S3FileSystem
import os

from hexa.catalog.models import (
    Base,
    Content,
    Datasource,
    CatalogIndex,
    CatalogIndexPermission,
    CatalogIndexType,
)
from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.models import Permission
from hexa.core.models.cryptography import EncryptedTextField
from hexa.plugins.connector_s3.api import generate_sts_buckets_credentials

from .sync import list_objects, sync_objects, sync_directories

METADATA_FILENAME = ".openhexa.json"


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
    default_region = models.CharField(max_length=200, default="")
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
        """Sync the bucket by querying the S3 API"""

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

        # Lock the bucket
        with transaction.atomic():
            Bucket.objects.select_for_update().get(pk=self.pk)
            # Sync data elements
            with transaction.atomic():
                objects = list(list_objects(self, fs, f"{self.s3_name}"))
                result = sync_directories(self, fs, objects)
                result += sync_objects(self, fs, objects)

                # Flag the datasource as synced
                self.last_synced_at = timezone.now()
                self.save()

        return result

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
        catalog_index, _ = CatalogIndex.objects.update_or_create(
            defaults={
                "last_synced_at": self.last_synced_at,
                "content_summary": self.content_summary,
                "owner": self.owner,
                "name": self.name,
                "external_name": self.s3_name,
                "countries": self.countries,
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            index_type=CatalogIndexType.DATASOURCE,
            detail_url=reverse("connector_s3:datasource_detail", args=(self.pk,)),
        )

        for permission in self.bucketpermission_set.all():
            CatalogIndexPermission.objects.get_or_create(
                catalog_index=catalog_index, team=permission.team
            )

    @property
    def display_name(self):
        return self.hexa_or_s3_name


class BucketPermission(Permission):
    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("bucket", "team")]

    def index_object(self):
        self.bucket.index()

    def __str__(self):
        return f"Permission for team '{self.team}' on bucket '{self.bucket}'"


class ObjectQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            bucket__bucketpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Object(Content):
    class Meta:
        verbose_name = "S3 Object"
        ordering = ["s3_key"]

    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    s3_dirname = models.TextField()
    s3_key = models.TextField()
    s3_size = models.PositiveBigIntegerField()
    s3_storage_class = models.CharField(max_length=200)  # TODO: choices
    s3_type = models.CharField(max_length=200)  # TODO: choices
    s3_last_modified = models.DateTimeField(null=True, blank=True)
    s3_etag = models.CharField(max_length=200, null=True, blank=True)
    orphan = models.BooleanField(default=False)

    objects = ObjectQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.s3_dirname is None:
            self.s3_dirname = self.compute_dirname(self.s3_key)
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        return self.name if self.name else self.s3_key

    @property
    def s3_extension(self):
        return os.path.splitext(self.s3_key)[1].lstrip(".")

    def index(self):  # TODO: fishy
        pass

    @classmethod
    def compute_dirname(cls, key):
        if key.endswith("/"):  # This is a directory
            return os.path.dirname(os.path.dirname(key)) + "/"
        else:  # This is a file
            return os.path.dirname(key) + "/"

    def update_metadata(self, object_data):
        self.orphan = False

        self.s3_key = object_data["Key"]
        self.s3_dirname = self.compute_dirname(object_data["Key"])
        self.s3_size = object_data["size"]
        self.s3_etag = object_data["ETag"]
        self.s3_storage_class = object_data["StorageClass"]
        self.s3_type = object_data["type"]
        self.s3_last_modified = object_data.get("LastModified")
        self.s3_etag = object_data.get("ETag")

    @classmethod
    def create_from_object_data(cls, bucket, object_data):
        # TODO: move to manager
        return cls.objects.create(
            bucket=bucket,
            s3_key=object_data["Key"],
            s3_dirname=cls.compute_dirname(object_data["Key"]),
            s3_size=object_data["size"],
            s3_storage_class=object_data["StorageClass"],
            s3_type=object_data["type"],
            s3_last_modified=object_data.get("LastModified"),
            s3_etag=object_data.get("ETag"),
        )
