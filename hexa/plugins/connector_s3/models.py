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
                result = self.sync_objects(fs)

                # Flag the datasource as synced
                self.last_synced_at = timezone.now()
                self.save()

        return result

    def list_objects(self, fs, path):
        for object_data in fs.ls(path, detail=True):
            if object_data["Key"][-1] == "/" and object_data["size"] == 0:
                # FIXME: What is this ?
                # FIXME: seems to be because directories appear in double
                # FIXME: once with a /, once without
                # TODO: check if safer way
                continue

            yield object_data

            if object_data["type"] == "directory":
                yield from self.list_objects(fs, object_data["Key"])

    def sync_objects(self, fs):
        existing = {x.s3_key: x for x in self.object_set.all()}

        created = {}
        updated_count = 0
        identical_count = 0
        merged_count = 0

        for object_data in self.list_objects(fs, f"{self.s3_name}"):
            key = object_data["Key"]

            if key in existing:
                if object_data["ETag"] == existing[key].s3_etag:
                    identical_count += 1
                else:
                    existing[key].update_from_data(object_data)
                    existing[key].save()
                    updated_count += 1
                del existing[key]
            else:
                created[key] = Object.objects.create(
                    bucket=self,
                    s3_key=object_data["Key"],
                    s3_size=object_data["size"],
                    s3_storage_class=object_data["StorageClass"],
                    s3_type=object_data["type"],
                    s3_name=object_data["name"],
                    s3_last_modified=object_data.get("LastModified"),
                    s3_etag=object_data["ETag"],
                )

        orphans_by_etag = {x.s3_etag: x for x in existing.values()}

        for created_obj in created.values():
            etag = created_obj.s3_etag
            orphan_obj = orphans_by_etag.get(etag)
            if orphan_obj:
                del orphans_by_etag[etag]
                orphan_obj.delete()
                # TODO: copy metadata from old to new
                merged_count += 1

        new_orphans_count = len([x for x in orphans_by_etag.values() if not x.orphan])

        for obj in orphans_by_etag.values():
            obj.orphan = True
            obj.save()

        results = DatasourceSyncResult(
            datasource=self,
            created=len(created) - merged_count,
            updated=updated_count + merged_count,
            identical=identical_count,
            orphaned=new_orphans_count,
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
    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)


class ObjectQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            bucket__bucketpermission__team__in=[t.pk for t in user.team_set.all()]
        )

    def filter_by_bucket_id_and_path(self, bucket_id: str, path: str):
        try:
            bucket = Bucket.objects.get(id=bucket_id)
        except Bucket.DoesNotExist:
            return self.none()

        if path == "/":
            parent = None
        else:
            try:
                parent = Object.objects.get(parent__s3_key=f"{bucket.s3_name}/{path}")
            except Object.DoesNotExist:
                return self.none()

        return self.filter(bucket=bucket, parent=parent)


class Object(Content):
    class Meta:
        verbose_name = "S3 Object"
        ordering = ["s3_key"]

    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE, blank=True)
    s3_key = models.TextField()
    s3_size = models.PositiveBigIntegerField()
    s3_storage_class = models.CharField(max_length=200)  # TODO: choices
    s3_type = models.CharField(max_length=200)  # TODO: choices
    s3_name = models.CharField(max_length=200)
    s3_last_modified = models.DateTimeField(null=True)
    s3_etag = models.CharField(max_length=200, null=True)
    orphan = models.BooleanField(default=False)

    objects = ObjectQuerySet.as_manager()

    @property
    def hexa_or_s3_name(self):
        return self.name if self.name != "" else self.s3_name

    @property
    def display_name(self):
        return self.hexa_or_s3_name

    @property
    def s3_extension(self):
        return os.path.splitext(self.s3_key)[1].lstrip(".")

    def index(self):  # TODO: fishy
        pass

    def update_from_data(self, object_data):
        self.orphan = False

        self.s3_size = object_data["size"]
        self.s3_etag = object_data["ETag"]
        # TODO: update other fields too
