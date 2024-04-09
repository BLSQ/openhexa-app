from __future__ import annotations

import os
import typing
from logging import getLogger

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.template.defaultfilters import filesizeformat, pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import Datasource, Entry
from hexa.catalog.queue import datasource_work_queue
from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.models.base import BaseQuerySet
from hexa.plugins.connector_s3.api import (
    S3ApiError,
    get_object_metadata,
    head_bucket,
    list_objects_metadata,
)
from hexa.plugins.connector_s3.region import AWSRegion
from hexa.user_management import models as user_management_models
from hexa.user_management.models import Permission, PermissionMode

logger = getLogger(__name__)


class BucketQuerySet(BaseQuerySet):
    def filter_for_user(
        self,
        user: AnonymousUser | user_management_models.User,
        mode: PermissionMode = None,
        mode__in: typing.Sequence[PermissionMode] = None,
    ):
        if mode is not None and mode__in is not None:
            raise ValueError('Please provide either "mode" or "mode_in" - not both')

        if not user.is_authenticated:
            return self.none()
        elif user.is_superuser:
            queryset = self.all()
        # Note about the join happening behind the scenes: we need to filter on team AND mode in the same filter call
        # (see https://docs.djangoproject.com/en/4.0/topics/db/queries/#spanning-multi-valued-relationships)
        elif mode is not None:
            queryset = self.filter(
                bucketpermission__team__in=user.team_set.all(),
                bucketpermission__mode=mode,
            )
        elif mode__in is not None:
            queryset = self.filter(
                bucketpermission__team__in=user.team_set.all(),
                bucketpermission__mode__in=mode__in,
            )
        else:
            queryset = self.filter(bucketpermission__team__in=user.team_set.all())

        # When querying for buckets with "VIEWER" permission mode, we want to exclude buckets for which the user has
        # higher privileges - otherwise the VIEWER mode will supersede EDITOR / OWNER modes in generated permissions
        if mode == PermissionMode.VIEWER or mode__in == [PermissionMode.VIEWER]:
            editor_or_owner_buckets = self.filter_for_user(
                user, mode__in=[PermissionMode.EDITOR, PermissionMode.OWNER]
            )
            queryset = queryset.exclude(id__in=[b.id for b in editor_or_owner_buckets])

        return queryset.distinct()


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
    searchable = True  # TODO: remove (see comment in datasource_index command)

    def refresh(self, path):
        metadata = get_object_metadata(
            bucket=self,
            object_key=path,
        )

        try:
            s3_object = Object.objects.get(bucket=self, key=path)
        except Object.DoesNotExist:
            Object.create_from_metadata(self, metadata)
        except Object.MultipleObjectsReturned:
            logger.warning(
                "Bucket.refresh(): incoherent object list for bucket %s", self.id
            )
        else:
            s3_object.update_from_metadata(metadata)
            s3_object.save()

    def clean(self):
        try:
            head_bucket(bucket=self)
        except S3ApiError as e:
            raise ValidationError(e)

    def sync(self):
        """Sync the bucket by querying the S3 API"""
        s3_objects = list_objects_metadata(
            bucket=self,
        )

        # Lock the bucket
        with transaction.atomic():
            Bucket.objects.select_for_update().get(pk=self.pk)
            # Sync data elements
            with transaction.atomic():
                created_count = 0
                updated_count = 0
                identical_count = 0
                deleted_count = 0

                remote = set()
                local = {str(x.key): x for x in self.object_set.all()}

                for s3_object in s3_objects:
                    key = s3_object["Key"]
                    remote.add(key)
                    if key in local:
                        if (
                            s3_object.get("ETag") == local[key].etag
                            and s3_object["Type"] == local[key].type
                        ):
                            # If it has the same key bot not the same ETag: the file was updated on S3
                            # (Sometime, the ETag contains double quotes -> strip them)
                            identical_count += 1
                        else:
                            updated_count += 1
                            local[key].update_from_metadata(s3_object)
                            local[key].save()
                    else:
                        Object.create_from_metadata(self, s3_object)
                        created_count += 1

                # cleanup unmatched objects
                for key, obj in local.items():
                    if key not in remote:
                        deleted_count += 1
                        obj.delete()
                # Flag the datasource as synced
                self.last_synced_at = timezone.now()
                self.save()

        return DatasourceSyncResult(
            datasource=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            deleted=deleted_count,
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
        index.datasource_name = self.name
        index.datasource_id = self.id

    def index_all_objects(self):
        logger.info("index_all_objects %s", self.id)
        for obj in self.object_set.all():
            try:
                with transaction.atomic():
                    obj.build_index()
            except Exception:
                logger.exception("index error")

    @property
    def display_name(self):
        return self.name

    def __str__(self):
        return self.display_name


class BucketPermission(Permission):
    class Meta(Permission.Meta):
        constraints = [
            models.UniqueConstraint(
                "team",
                "bucket",
                name="bucket_unique_team",
                condition=Q(team__isnull=False),
            ),
            models.UniqueConstraint(
                "user",
                "bucket",
                name="bucket_unique_user",
                condition=Q(user__isnull=False),
            ),
            models.CheckConstraint(
                check=Q(team__isnull=False) | Q(user__isnull=False),
                name="bucket_permission_user_or_team_not_null",
            ),
        ]

    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)

    def index_object(self):
        self.bucket.build_index()
        datasource_work_queue.enqueue(
            "datasource_index",
            {
                "contenttype_id": ContentType.objects.get_for_model(self.bucket).id,
                "object_id": str(self.bucket.id),
            },
        )

    def __str__(self):
        return f"Permission for team '{self.team}' on bucket '{self.bucket}'"


class ObjectQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | user_management_models.User):
        return self.filter(bucket__in=Bucket.objects.filter_for_user(user))


class Object(Entry):
    def get_permission_set(self):
        return self.bucket.bucketpermission_set.all()

    class Meta:
        verbose_name = "S3 Object"
        ordering = ("key",)
        unique_together = [("bucket", "key")]

    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)
    key = models.TextField()
    parent_key = models.TextField()
    size = models.PositiveBigIntegerField()
    storage_class = models.CharField(max_length=200)  # TODO: choices
    type = models.CharField(max_length=200)  # TODO: choices
    last_modified = models.DateTimeField(null=True, blank=True)
    etag = models.CharField(max_length=200, null=True, blank=True)

    objects = ObjectQuerySet.as_manager()
    searchable = True  # TODO: remove (see comment in datasource_index command)

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
        index.datasource_name = self.bucket.name
        index.datasource_id = self.bucket.id

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

    @property
    def download_url(self):
        if self.bucket.public:
            return f"https://{self.bucket.name}.s3.{self.bucket.region}.amazonaws.com/{self.key}"
        else:
            return reverse(
                "connector_s3:object_download",
                kwargs={"bucket_id": self.bucket.id, "path": self.key},
            )

    def update_from_metadata(self, metadata):
        self.key = metadata["Key"]
        self.parent_key = self.compute_parent_key(metadata["Key"])
        self.size = metadata["Size"]
        self.storage_class = metadata["StorageClass"]
        self.type = metadata["Type"]
        self.last_modified = metadata["LastModified"]
        self.etag = metadata["ETag"]

    @classmethod
    def create_from_metadata(cls, bucket, metadata):
        return cls.objects.create(
            bucket=bucket,
            key=metadata["Key"],
            parent_key=cls.compute_parent_key(metadata["Key"]),
            storage_class=metadata["StorageClass"],
            last_modified=metadata["LastModified"],
            etag=metadata["ETag"],
            type=metadata["Type"],
            size=metadata["Size"],
        )
