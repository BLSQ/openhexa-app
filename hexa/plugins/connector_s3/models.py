import os
from collections import defaultdict
from logging import getLogger
from typing import Dict, List

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template.defaultfilters import filesizeformat, pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from s3fs import S3FileSystem

from hexa.catalog.models import CatalogQuerySet, Datasource, Entry
from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.models import Base, Permission
from hexa.core.models.cryptography import EncryptedTextField
from hexa.plugins.connector_s3.api import (
    S3ApiError,
    generate_sts_app_s3_credentials,
    get_object_info,
    head_bucket,
)
from hexa.plugins.connector_s3.region import AWSRegion

logger = getLogger(__name__)


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
    default_region = models.CharField(
        max_length=50, default=AWSRegion.EU_CENTRAL_1, choices=AWSRegion.choices
    )
    user_arn = models.CharField(max_length=200)
    app_role_arn = models.CharField(max_length=200)

    @property
    def display_name(self):
        return self.username


class BucketPermissionMode(models.IntegerChoices):
    READ_ONLY = 1, "Read Only"
    READ_WRITE = 2, "Read Write"


class BucketQuerySet(CatalogQuerySet):
    def filter_by_mode(self, user, mode: BucketPermissionMode = None):
        if user.is_active and user.is_superuser:
            # if SU -> all buckets are RW; so if mode is provided and mode == RO -> no buckets available
            if mode == BucketPermissionMode.READ_ONLY:
                return self.none()
            else:
                return self

        if mode is None:
            # return all buckets
            modes = [BucketPermissionMode.READ_ONLY, BucketPermissionMode.READ_WRITE]
        else:
            modes = [mode]

        return self.filter(
            bucketpermission__team__in=[t.pk for t in user.team_set.all()],
            bucketpermission__mode__in=modes,
        ).distinct()

    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            bucketpermission__team__in=[t.pk for t in user.team_set.all()],
        ).distinct()


class Bucket(Datasource):
    def get_permission_set(self):
        return self.bucketpermission_set.all()

    class Meta:
        verbose_name = "S3 Bucket"
        ordering = ("name",)

    name = models.CharField(max_length=200)
    region = models.CharField(
        max_length=50, default=AWSRegion.EU_CENTRAL_1, choices=AWSRegion.choices
    )

    objects = BucketQuerySet.as_manager()

    @property
    def principal_credentials(self):
        try:
            return Credentials.objects.get()
        except (Credentials.DoesNotExist, Credentials.MultipleObjectsReturned):
            raise ValidationError(
                "The S3 connector plugin should be configured with a single Credentials entry"
            )

    def refresh(self, path):
        info = get_object_info(
            principal_credentials=self.principal_credentials,
            bucket=self,
            object_key=path,
        )

        # extend info -> not all things from s3fs present in boto3 API
        info["type"] = "file"  # no concept of directory from boto3 API
        info["true_key"] = path

        try:
            object = Object.objects.get(bucket=self, key=path, orphan=False)
        except Object.DoesNotExist:
            Object.create_from_object_data(self, info)
        except Object.MultipleObjectsReturned:
            logger.warning(
                "Bucket.refresh(): incoherent object list for bucket %s", self.id
            )
        else:
            object.update_metadata(info)
            object.save()

    def clean(self):
        try:
            head_bucket(principal_credentials=self.principal_credentials, bucket=self)
        except S3ApiError as e:
            raise ValidationError(e)

    def sync(self):  # TODO: move in api/sync module
        """Sync the bucket by querying the S3 API"""

        sts_credentials = generate_sts_app_s3_credentials(
            principal_credentials=self.principal_credentials,
            bucket=self,
        )
        fs = S3FileSystem(
            key=sts_credentials["AccessKeyId"],
            secret=sts_credentials["SecretAccessKey"],
            token=sts_credentials["SessionToken"],
        )
        fs.invalidate_cache()

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
            # S3fs adds the bucket name in the Key, we remove it to be consistent with the S3 documentation
            object_data["true_key"] = object_data["Key"].split("/", 1)[1]

            if object_data["Key"] == f"{path}" and object_data["type"] != "directory":
                # Detects the current directory. Ignore it as we already got it from the parent listing
                continue

            # Manually add a / at the end of the directory paths to be more POSIX-compliant
            if object_data["type"] == "directory" and not object_data["Key"].endswith(
                "/"
            ):
                object_data["Key"] = object_data["Key"] + "/"
                object_data["true_key"] = object_data["true_key"] + "/"

            # ETag seems to sometimes contain quotes, probably because of a bug in s3fs
            if object_data.get("ETag", "").startswith('"'):
                object_data["ETag"] = object_data["ETag"].replace('"', "")

            yield object_data

            if object_data["type"] == "directory":
                yield from self.list_objects(fs, object_data["Key"])

    def sync_directories(self, fs, s3_objects):
        created_count = 0
        updated_count = 0
        identical_count = 0
        new_orphans_count = 0

        existing_directories_by_key = {
            str(x.key): x for x in self.object_set.filter(type="directory")
        }

        for s3_obj in s3_objects:
            if s3_obj["type"] == "directory":
                s3_key = s3_obj["true_key"]
                existing = existing_directories_by_key.get(s3_key)
                if existing:
                    identical_count += 1
                    if existing.orphan:
                        existing.orphan = False
                        existing.save()
                    del existing_directories_by_key[s3_key]
                else:  # Not in the DB yet
                    Object.create_from_object_data(self, s3_obj)
                    created_count += 1

        for obj in existing_directories_by_key.values():
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

        existing_by_etag: Dict[str, List[Object]] = defaultdict(lambda: [])
        for obj in existing_by_key.values():
            existing_by_etag[obj.etag].append(obj)

        appeared_on_s3 = []
        touched = set()

        updated_count = 0
        identical_count = 0
        created_count = 0
        orphaned_count = 0

        for object_data in discovered_objects:
            if object_data["type"] != "file":
                continue

            key = object_data["true_key"]
            if key.endswith("/.openhexa.json"):
                continue

            # If we know this file
            if key in existing_by_key:
                existing = existing_by_key[key]
                # If it was an orphan: it re-appeared at the same place on S3
                if existing.orphan:
                    existing.orphan = False
                # If it has the same key and same ETag: nothing changed
                if object_data.get("ETag") == existing_by_key[key].etag:
                    identical_count += 1
                # If it has the same key bot not the same ETag: the file was updated on S3
                else:
                    existing_by_key[key].update_metadata(object_data)
                    updated_count += 1

                touched.add(key)
                existing.save()

            # Else we never heard of this key before
            else:
                # keep it for later
                appeared_on_s3.append(object_data)

        # Now that we updated all files we already had in OpenHexa, we can try to match "new" files on S3 with
        # files in OH that are orphans
        for object_data in appeared_on_s3:
            # Do we have something in the DB that has the same ETag ?
            same_etags = existing_by_etag[object_data.get("ETag")]
            match = False
            if same_etags:
                for obj in same_etags:
                    # Find the first object in the DB that we did not touch
                    if obj.key not in touched:
                        # We found an orphan that matches our S3 file
                        match = True
                        updated_count += 1
                        obj.update_metadata(object_data)
                        touched.add(obj.key)
                        obj.save()

            # We found no match, we create a new record in the DB
            if not match:
                Object.create_from_object_data(self, object_data)
                created_count += 1

        # Now we iterate on all objects we had in the DB and if we did not encounter
        # them above, then they must be orphans
        for obj in existing_objects:
            if obj.key not in touched:
                if not obj.orphan:
                    obj.orphan = True
                    orphaned_count += 1
                    obj.save()

        return DatasourceSyncResult(
            datasource=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            orphaned=orphaned_count,
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

    def populate_index(self, index):
        index.last_synced_at = self.last_synced_at
        index.content = self.content_summary
        index.path = [self.pk.hex]
        index.external_id = self.name
        index.external_name = self.name
        index.external_type = "bucket"
        index.search = f"{self.name}"

    @property
    def display_name(self):
        return self.name

    def __str__(self):
        return self.display_name

    def writable_by(self, user):
        if not user.is_active:
            return False
        elif user.is_superuser:
            return True
        elif (
            BucketPermission.objects.filter(
                bucket=self,
                team_id__in=user.team_set.all().values("id"),
                mode=BucketPermissionMode.READ_WRITE,
            ).count()
            > 0
        ):
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse(
            "connector_s3:datasource_detail", kwargs={"datasource_id": self.id}
        )


class BucketPermission(Permission):
    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    mode = models.IntegerField(
        choices=BucketPermissionMode.choices, default=BucketPermissionMode.READ_WRITE
    )

    class Meta:
        unique_together = [("bucket", "team")]

    def index_object(self):
        self.bucket.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on bucket '{self.bucket}'"


class ObjectQuerySet(CatalogQuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(bucket__in=Bucket.objects.filter_for_user(user))


class Object(Entry):
    def get_permission_set(self):
        return self.bucket.bucketpermission_set.all()

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

    def populate_index(self, index):
        index.last_synced_at = self.bucket.last_synced_at
        index.external_name = self.filename
        index.path = [self.bucket.pk.hex, self.pk.hex]
        index.context = self.parent_key
        index.external_id = self.key
        index.external_type = self.type
        index.external_subtype = self.extension
        index.search = f"{self.filename} {self.key}"

    def __repr__(self):
        return f"<Object s3://{self.bucket.name}/{self.key}>"

    @property
    def display_name(self):
        return self.filename

    @property
    def filename(self):
        if self.key.endswith("/"):
            return os.path.basename(self.key[:-1])
        return os.path.basename(self.key)

    @property
    def extension(self):
        return os.path.splitext(self.key)[1].lstrip(".")

    def full_path(self):
        return f"s3://{self.bucket.name}/{self.key}"

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
        else:
            if verbose_file_type := self.verbose_file_type:
                return verbose_file_type
            else:
                return _("File")

    @property
    def verbose_file_type(self):
        file_type = {
            "xlsx": "Excel file",
            "md": "Markdown document",
            "ipynb": "Jupyter Notebook",
            "csv": "CSV file",
        }.get(self.extension)
        if file_type:
            return _(file_type)
        else:
            return None

    def update_metadata(self, object_data):
        self.orphan = False

        self.key = object_data["true_key"]
        self.parent_key = self.compute_parent_key(object_data["true_key"])
        if "size" in object_data:
            self.size = object_data["size"]
        elif "ContentLength" in object_data:
            self.size = object_data["ContentLength"]
        else:
            raise KeyError("size")
        self.storage_class = object_data.get("StorageClass", "STANDARD")
        self.type = object_data["type"]
        self.last_modified = object_data.get("LastModified")
        self.etag = object_data.get("ETag")
        if self.etag and self.etag.startswith('"'):
            self.etag.strip('"')
        self.orphan = False

    @classmethod
    def create_from_object_data(cls, bucket, object_data):
        if "size" in object_data:
            size = object_data["size"]
        elif "ContentLength" in object_data:
            size = object_data["ContentLength"]
        else:
            raise KeyError("size")

        # TODO: move to manager
        return cls.objects.create(
            bucket=bucket,
            key=object_data["true_key"],
            parent_key=cls.compute_parent_key(object_data["true_key"]),
            storage_class=object_data.get("StorageClass", "STANDARD"),
            last_modified=object_data.get("LastModified"),
            etag=object_data["ETag"].strip('"') if "ETag" in object_data else None,
            type=object_data["type"],
            size=size,
        )

    def get_absolute_url(self):
        return reverse(
            "connector_s3:object_detail",
            kwargs={"bucket_id": self.bucket.id, "path": self.key},
        )
