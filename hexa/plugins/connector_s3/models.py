import os
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
                objects = list(self.list_objects(fs, f"{self.s3_name}"))
                result = self.sync_directories(fs, objects)
                result += self.sync_objects(fs, objects)

                # Flag the datasource as synced
                self.last_synced_at = timezone.now()
                self.save()

        return result

    def list_objects(self, fs, path):
        for object_data in fs.ls(path, detail=True):
            if object_data["Key"] == f"{path}/" and object_data["type"] != "directory":
                # Detects the current directory. Ignore it as we already got it from the parent listing
                continue

            # Manually add a / at the end of the directory paths to be more POSIX-compliant
            if object_data["type"] == "directory" and not object_data["Key"].endswith(
                "/"
            ):
                object_data["Key"] = object_data["Key"] + "/"

            # ETag seems to sometimes contain quotes, probably because of a bug in s3fs
            if "ETag" in object_data and object_data["ETag"].startswith('"'):
                object_data["ETag"] = object_data["ETag"].replace('"', "")

            yield object_data

            if object_data["type"] == "directory":
                yield from self.list_objects(fs, object_data["Key"])

    def sync_directories(self, fs, s3_objects):
        created_count = 0
        updated_count = 0
        identical_count = 0
        new_orphans_count = 0

        existing_directories_by_uid = {
            str(x.id): x for x in self.object_set.filter(s3_type="directory")
        }

        for s3_obj in s3_objects:
            if s3_obj["type"] == "directory":
                metadata_path = os.path.join(s3_obj["Key"], METADATA_FILENAME)
                s3_uid = None
                if fs.exists(metadata_path):
                    with fs.open(metadata_path, mode="rb") as fd:
                        try:
                            metadata = json.load(fd)
                            s3_uid = metadata.get("uid")
                        except json.decoder.JSONDecodeError:
                            pass

                db_obj = existing_directories_by_uid.get(s3_uid)
                if db_obj:
                    if db_obj.s3_key != s3_obj["Key"]:  # Directory moved
                        db_obj.update_metadata(s3_obj)
                        db_obj.save()
                        updated_count += 1
                    else:  # Not moved
                        identical_count += 1
                    del existing_directories_by_uid[s3_uid]
                else:  # Not in the DB yet
                    db_obj = Object.create_from_object_data(self, s3_obj)
                    metadata_path = os.path.join(db_obj.s3_key, METADATA_FILENAME)
                    with fs.open(metadata_path, mode="wb") as fd:
                        fd.write(json.dumps({"uid": str(db_obj.id)}).encode())
                    created_count += 1

        for obj in existing_directories_by_uid.values():
            if not obj.orphan:
                new_orphans_count += 1
                obj.orphan = True
                obj.save()

        return DatasourceSyncResult(
            datasource=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            orphaned=new_orphans_count,
        )

    def sync_objects(self, fs, discovered_objects):
        existing_objects = list(self.object_set.filter(s3_type="file"))
        existing_by_key = {x.s3_key: x for x in existing_objects}

        created = {}
        updated_count = 0
        identical_count = 0
        merged_count = 0

        for object_data in discovered_objects:
            if object_data["type"] != "file":
                continue
            key = object_data["Key"]
            if key.endswith("/.openhexa.json"):
                continue

            if key in existing_by_key:
                if object_data.get("ETag") == existing_by_key[key].s3_etag:
                    identical_count += 1
                else:
                    existing_by_key[key].update_metadata(object_data)
                    existing_by_key[key].save()
                    updated_count += 1
                del existing_by_key[key]
            else:
                created[key] = Object.create_from_object_data(self, object_data)

        orphans_by_etag = {x.s3_etag: x for x in existing_by_key.values()}

        for created_obj in created.values():
            etag = created_obj.s3_etag
            orphan_obj = orphans_by_etag.get(etag)
            if orphan_obj:
                del orphans_by_etag[etag]
                orphan_obj.delete()
                merged_count += 1

        new_orphans_count = len([x for x in orphans_by_etag.values() if not x.orphan])

        for obj in orphans_by_etag.values():
            obj.orphan = True
            obj.save()

        return DatasourceSyncResult(
            datasource=self,
            created=len(created) - merged_count,
            updated=updated_count + merged_count,
            identical=identical_count,
            orphaned=new_orphans_count,
        )

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
    s3_last_modified = models.DateTimeField(null=True, blank=True)
    s3_etag = models.CharField(max_length=200, null=True, blank=True)
    orphan = models.BooleanField(default=False)

    objects = ObjectQuerySet.as_manager()

    @property
    def display_name(self):
        return self.name if self.name else self.s3_key

    @property
    def s3_extension(self):
        return os.path.splitext(self.s3_key)[1].lstrip(".")

    def index(self):  # TODO: fishy
        pass

    def update_metadata(self, object_data):
        self.orphan = False

        self.s3_key = object_data["Key"]
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
            s3_size=object_data["size"],
            s3_storage_class=object_data["StorageClass"],
            s3_type=object_data["type"],
            s3_last_modified=object_data.get("LastModified"),
            s3_etag=object_data.get("ETag"),
        )
