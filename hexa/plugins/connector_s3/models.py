import json

import boto3
from botocore.exceptions import ClientError
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import filesizeformat

from s3fs import S3FileSystem
import os

from hexa.catalog.models import (
    Base,
    Datasource,
    Entry,
    Index,
    IndexPermission,
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
        ordering = ("name",)

    name = models.CharField(max_length=200)

    objects = BucketQuerySet.as_manager()

    def clean(self):
        try:
            principal_s3_credentials = Credentials.objects.get()
        except (Credentials.DoesNotExist, Credentials.MultipleObjectsReturned):
            raise ValidationError(
                "Ensure the S3 connector plugin first has a single credentials entry"
            )

        sts_credentials = generate_sts_buckets_credentials(
            user=None,
            principal_credentials=principal_s3_credentials,
            buckets=[self],
            duration=900,
        )
        client = boto3.client(
            "s3",
            aws_access_key_id=sts_credentials["AccessKeyId"],
            aws_secret_access_key=sts_credentials["SecretAccessKey"],
            aws_session_token=sts_credentials["SessionToken"],
        )
        try:
            client.head_bucket(Bucket=self.name)
        except ClientError as e:
            raise ValidationError(e)

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
                objects = list(self.list_objects(fs, f"{self.name}"))
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
            str(x.id): x for x in self.object_set.filter(type="directory")
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
                    if db_obj.key != s3_obj["Key"]:  # Directory moved
                        db_obj.update_metadata(s3_obj)
                        db_obj.save()
                        updated_count += 1
                    else:  # Not moved
                        identical_count += 1
                    del existing_directories_by_uid[s3_uid]
                else:  # Not in the DB yet
                    db_obj = Object.create_from_object_data(self, s3_obj)
                    metadata_path = os.path.join(db_obj.key, METADATA_FILENAME)
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
        existing_objects = list(self.object_set.filter(type="file"))
        existing_by_key = {x.key: x for x in existing_objects}

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
                if object_data.get("ETag") == existing_by_key[key].etag:
                    identical_count += 1
                    existing_by_key[key].save()
                else:
                    existing_by_key[key].update_metadata(object_data)
                    existing_by_key[key].save()
                    updated_count += 1
                del existing_by_key[key]
            else:
                created[key] = Object.create_from_object_data(self, object_data)

        orphans_by_etag = {x.etag: x for x in existing_by_key.values()}

        for created_obj in created.values():
            etag = created_obj.etag
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
        index, _ = Index.objects.update_or_create(
            defaults={
                "last_synced_at": self.last_synced_at,
                "path": self.pk.hex,
                "external_id": self.name,
                "external_name": self.name,
                "external_type": "bucket",
                "search": f"{self.name}",
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )

        for permission in self.bucketpermission_set.all():
            IndexPermission.objects.get_or_create(index=index, team=permission.team)

    @property
    def display_name(self):
        return self.name


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


class Object(Entry):
    class Meta:
        verbose_name = "S3 Object"
        ordering = ("key",)

    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    key = models.TextField()
    parent_key = models.TextField()
    size = models.PositiveBigIntegerField()
    storage_class = models.CharField(max_length=200)  # TODO: choices
    type = models.CharField(max_length=200)  # TODO: choices
    last_modified = models.DateTimeField(null=True, blank=True)
    etag = models.CharField(max_length=200, null=True, blank=True)
    orphan = models.BooleanField(default=False)  # TODO: remove?

    objects = ObjectQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.parent_key is None:
            self.parent_key = self.compute_parent_key(self.key)
        super().save(*args, **kwargs)

    def index(self):
        index, _ = Index.objects.update_or_create(
            defaults={
                "last_synced_at": self.bucket.last_synced_at,
                "external_name": self.filename,
                "path": f"{self.bucket.pk.hex}.{self.pk.hex}",
                "context": self.parent_key,
                "external_id": self.key,
                "external_type": self.type,
                "external_subtype": self.extension,
                "search": f"{self.filename} {self.key}",
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
        )

        for permission in self.bucket.bucketpermission_set.all():
            IndexPermission.objects.get_or_create(index=index, team=permission.team)

    @property
    def display_name(self):
        return self.filename

    @property
    def filename(self):
        return os.path.basename(self.key)

    @property
    def extension(self):
        return os.path.splitext(self.key)[1].lstrip(".")

    @classmethod
    def compute_parent_key(cls, key):
        if key.endswith("/"):  # This is a directory
            return os.path.dirname(os.path.dirname(key)) + "/"
        else:  # This is a file
            return os.path.dirname(key) + "/"

    @property
    def file_size_display(self):
        return filesizeformat(self.size) if self.size > 0 else "-"

    @property
    def type_display(self):
        if self.type == "directory":
            return _("Directory")

        file_type = {
            "xlsx": "Excel file",
            "md": "Markdown document",
            "ipynb": "Jupyter Notebook",
            "csv": "CSV file",
        }.get(self.extension, "File")

        return _(file_type)

    def update_metadata(self, object_data):
        self.orphan = False

        self.key = object_data["Key"]
        self.parent_key = self.compute_parent_key(object_data["Key"])
        self.size = object_data["size"]
        self.etag = object_data["ETag"]
        self.storage_class = object_data["StorageClass"]
        self.type = object_data["type"]
        self.last_modified = object_data.get("LastModified")
        self.etag = object_data.get("ETag")

    @classmethod
    def create_from_object_data(cls, bucket, object_data):
        # TODO: move to manager
        return cls.objects.create(
            bucket=bucket,
            key=object_data["Key"],
            parent_key=cls.compute_parent_key(object_data["Key"]),
            size=object_data["size"],
            storage_class=object_data["StorageClass"],
            type=object_data["type"],
            last_modified=object_data.get("LastModified"),
            etag=object_data.get("ETag"),
        )
