import logging
import math
import secrets
from functools import cached_property

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from dpq.models import BaseJob
from slugify import slugify

from hexa.core.models.base import Base, BaseQuerySet
from hexa.datasets.api import get_blob
from hexa.metadata.models import MetadataMixin
from hexa.user_management.models import User

logger = logging.getLogger(__name__)


def create_dataset_slug(name: str, workspace):
    suffix = ""
    while True:
        slug = slugify(name[: 255 - len(suffix)] + suffix)
        if not Dataset.objects.filter(workspace=workspace, slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)


class DatasetQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self._filter_for_user_and_query_object(
                user, models.Q(links__workspace=user.pipeline_run.pipeline.workspace)
            )
        else:
            return self._filter_for_user_and_query_object(
                user,
                models.Q(links__workspace__members=user),
                return_all_if_superuser=False,
            )


class DatasetManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: any,
        *,
        name: str,
        description: str,
    ):
        from hexa.pipelines.authentication import PipelineRunUser

        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        if isinstance(principal, PipelineRunUser):
            if principal.pipeline_run.pipeline.workspace != workspace:
                raise PermissionDenied
        elif not principal.has_perm("datasets.create_dataset", workspace):
            raise PermissionDenied

        created_by = principal if not isinstance(principal, PipelineRunUser) else None
        dataset = self.create(
            workspace=workspace,
            slug=create_dataset_slug(name, workspace),
            created_by=created_by,
            name=name,
            description=description,
        )
        # Create the DatasetLink for the workspace
        dataset.link(created_by, workspace)

        return dataset


class Dataset(MetadataMixin, Base):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "slug",
                name="unique_dataset_slug_per_workspace",
            )
        ]

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.TextField(max_length=64, null=False, blank=False)
    slug = models.TextField(null=False, blank=False, max_length=255)
    description = models.TextField(blank=True, null=True)

    objects = DatasetManager.from_queryset(DatasetQuerySet)()

    @property
    def latest_version(self):
        return self.versions.order_by("-created_at").first()

    def update_if_has_perm(self, *, principal: User, **kwargs):
        if not principal.has_perm("datasets.update_dataset", self):
            raise PermissionDenied

        for key in ["name", "description"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("datasets.delete_dataset", self):
            raise PermissionDenied
        self.delete()

    def create_version(self, *, principal: User, name: str, changelog: str = None):
        return DatasetVersion.objects.create_if_has_perm(
            principal=principal,
            dataset=self,
            name=name,
            changelog=changelog,
        )

    def can_view_metadata(self, user: User):
        if not user.has_perm("datasets.view_dataset", self):
            raise PermissionDenied
        return True

    def can_update_metadata(self, user: User):
        if not user.has_perm("datasets.update_dataset", self):
            raise PermissionDenied
        return True

    def can_delete_metadata(self, user: User):
        if not user.has_perm("datasets.update_dataset", self):
            raise PermissionDenied
        return True

    def link(self, principal: User, workspace: any):
        return DatasetLink.objects.create(
            created_by=principal,
            dataset=self,
            workspace=workspace,
        )


class DatasetVersionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        # TODO: It should also check workspace where it's added
        return self._filter_for_user_and_query_object(
            user,
            models.Q(dataset__in=Dataset.objects.filter_for_user(user)),
            return_all_if_superuser=False,
        )


class DatasetVersionManager(models.Manager):
    def create_if_has_perm(
        self, principal: User, dataset: Dataset, *, name: str, changelog: str
    ):
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(principal, PipelineRunUser):
            if principal.pipeline_run.pipeline.workspace != dataset.workspace:
                raise PermissionDenied
        elif not principal.has_perm("datasets.create_dataset_version", dataset):
            raise PermissionDenied
        created_by = principal if not isinstance(principal, PipelineRunUser) else None
        pipeline_run = (
            principal.pipeline_run if isinstance(principal, PipelineRunUser) else None
        )
        version = self.create(
            name=name,
            dataset=dataset,
            created_by=created_by,
            changelog=changelog,
            pipeline_run=pipeline_run,
        )

        return version


class DatasetVersion(MetadataMixin, Base):
    dataset = models.ForeignKey(
        Dataset,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    name = models.TextField(null=False, blank=False)
    changelog = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    pipeline_run = models.ForeignKey(
        "pipelines.PipelineRun",
        null=True,
        on_delete=models.SET_NULL,
        related_name="dataset_versions",
    )

    objects = DatasetVersionManager.from_queryset(DatasetVersionQuerySet)()

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("dataset", "name")

    def update_if_has_perm(self, *, principal: User, **kwargs):
        if not principal.has_perm("datasets.update_dataset_version", self):
            raise PermissionDenied

        for key in ["name", "changelog"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("datasets.delete_dataset_version", self):
            raise PermissionDenied
        self.delete()

    def can_view_metadata(self, user: User):
        if not user.has_perm("datasets.view_dataset_version", self):
            raise PermissionDenied
        return True

    def can_update_metadata(self, user: User):
        if not user.has_perm("datasets.update_dataset_version", self):
            raise PermissionDenied
        return True

    def can_delete_metadata(self, user: User):
        if not user.has_perm("datasets.delete_dataset_version", self):
            raise PermissionDenied
        return True

    def get_full_uri(self, file_uri):
        return f"{self.dataset.id}/{self.id}/{file_uri.lstrip('/')}"

    def get_file_by_name(self, name: str):
        return DatasetVersionFile.objects.get(
            dataset_version=self, uri=self.get_full_uri(name)
        )


class DatasetVersionFileQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            models.Q(
                dataset_version__dataset__in=Dataset.objects.filter_for_user(user)
            ),
            return_all_if_superuser=False,
        )

    def filter_by_filename(self, filename: str):
        return self.filter(uri__endswith=f"/{filename}")


class DatasetVersionFileManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        dataset_version: DatasetVersion,
        *,
        uri: str,
        content_type: str,
    ):
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(principal, PipelineRunUser):
            if (
                principal.pipeline_run.pipeline.workspace
                != dataset_version.dataset.workspace
            ):
                raise PermissionDenied
        elif not principal.has_perm(
            "datasets.create_dataset_version_file", dataset_version
        ):
            raise PermissionDenied

        created_by = principal if not isinstance(principal, PipelineRunUser) else None

        return self.create(
            dataset_version=dataset_version,
            uri=uri,
            content_type=content_type,
            created_by=created_by,
        )


class DatasetVersionFile(MetadataMixin, Base):
    uri = models.TextField(null=False, blank=False, unique=True)
    content_type = models.TextField(null=False, blank=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    properties = JSONField(default=dict)
    dataset_version = models.ForeignKey(
        DatasetVersion,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="files",
    )

    objects = DatasetVersionFileManager.from_queryset(DatasetVersionFileQuerySet)()

    def can_view_metadata(self, user: User):
        if not user.has_perm("datasets.view_dataset_version_file", self):
            raise PermissionDenied
        return True

    def can_update_metadata(self, user: User):
        if not user.has_perm("datasets.update_dataset_version_file", self):
            raise PermissionDenied
        return True

    def can_delete_metadata(self, user: User):
        if not user.has_perm("datasets.delete_dataset_version_file", self):
            raise PermissionDenied
        return True

    @property
    def filename(self):
        return self.uri.split("/")[-1]

    @property
    def sample_entry(self):
        return self.samples.first()

    @property
    def full_uri(self):
        return self.dataset_version.get_full_uri(self.uri)

    @cached_property
    def size(self):
        blob = get_blob(self.uri)
        if blob is None:
            return 0
        return blob.size

    def generate_metadata(self):
        from hexa.datasets.queue import dataset_file_metadata_queue

        dataset_file_metadata_queue.enqueue(
            "generate_file_metadata",
            {
                "file_id": str(self.id),
            },
        )

    class Meta:
        ordering = ["uri"]


class DataframeJsonEncoder(DjangoJSONEncoder):
    def encode(self, obj):
        # Recursively replace NaN with None (since it's a float, it does not call 'default' method)
        def custom_encoding(item):
            SKIPPED_FIELD = "<SKIPPED_BYTES>"

            if isinstance(item, float) and math.isnan(item):
                return None
            elif isinstance(item, dict):
                return {key: custom_encoding(value) for key, value in item.items()}
            elif isinstance(item, list):
                return [custom_encoding(element) for element in item]
            elif isinstance(item, bytes):
                return SKIPPED_FIELD
            return item

        # Preprocess the object to replace NaN values with None and encode bytes to base64
        obj = custom_encoding(obj)
        # Use the superclass's encode method to serialize the preprocessed object
        return super().encode(obj)


class DatasetFileSample(Base):
    STATUS_PROCESSING = "PROCESSING"
    STATUS_FAILED = "FAILED"
    STATUS_FINISHED = "FINISHED"

    STATUS_CHOICES = [
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_FAILED, _("Failed")),
        (STATUS_FINISHED, _("Finished")),
    ]
    sample = JSONField(
        blank=True,
        default=list,
        null=True,
        encoder=DataframeJsonEncoder,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PROCESSING,
    )
    status_reason = models.TextField(blank=True, null=True)
    dataset_version_file = models.ForeignKey(
        DatasetVersionFile,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="samples",
    )

    class Meta:
        ordering = ["-created_at"]


class DatasetLinkQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self._filter_for_user_and_query_object(
                user,
                models.Q(workspace=user.pipeline_run.pipeline.workspace),
            )
        else:
            return self._filter_for_user_and_query_object(
                user,
                models.Q(workspace__members=user),
                return_all_if_superuser=False,
            )


class DatasetLink(Base):
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="links")
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="+",
    )
    is_pinned = models.BooleanField(default=False, null=False, blank=False)

    objects = DatasetLinkQuerySet.as_manager()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("datasets.delete_linked_dataset", self):
            raise PermissionDenied
        self.delete()

    class Meta:
        unique_together = ("dataset", "workspace")


class DatasetFileMetadataJob(BaseJob):
    class Meta:
        db_table = "datasets_filemetadata_job"
