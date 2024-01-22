import secrets
import typing

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models
from slugify import slugify

from hexa.core.models.base import Base, BaseQuerySet
from hexa.user_management.models import User


def create_dataset_slug(name: str):
    suffix = secrets.token_hex(3)
    prefix = slugify(name[: 64 - 3])
    return prefix[:23].rstrip("-") + "-" + suffix


class DatasetQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
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
            slug=create_dataset_slug(name),
            created_by=created_by,
            name=name,
            description=description,
        )
        # Create the DatasetLink for the workspace
        dataset.link(created_by, workspace)

        return dataset


class Dataset(Base):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.TextField(max_length=64, null=False, blank=False)
    slug = models.TextField(null=False, blank=False, unique=True)
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

    def create_version(self, *, principal: User, name: str, description: str = None):
        return DatasetVersion.objects.create_if_has_perm(
            principal=principal,
            dataset=self,
            name=name,
            description=description,
        )

    def link(self, principal: User, workspace: any):
        return DatasetLink.objects.create(
            created_by=principal,
            dataset=self,
            workspace=workspace,
        )


class DatasetVersionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        # TODO: It should also check workspace where it's added
        return self._filter_for_user_and_query_object(
            user,
            models.Q(dataset__in=Dataset.objects.filter_for_user(user)),
            return_all_if_superuser=False,
        )


class DatasetVersionManager(models.Manager):
    def create_if_has_perm(
        self, principal: User, dataset: Dataset, *, name: str, description: str
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
            description=description,
            pipeline_run=pipeline_run,
        )

        return version


class DatasetVersion(Base):
    dataset = models.ForeignKey(
        Dataset,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    name = models.TextField(null=False, blank=False)
    description = models.TextField(blank=True, null=True)
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

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("datasets.delete_dataset_version", self):
            raise PermissionDenied
        self.delete()

    def get_full_uri(self, file_uri):
        return f"{self.dataset.id}/{self.id}/{file_uri.lstrip('/')}"

    def get_file_by_name(self, name: str):
        return DatasetVersionFile.objects.get(
            dataset_version=self, uri=self.get_full_uri(name)
        )


class DatasetVersionFileQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            models.Q(
                dataset_version__dataset__in=Dataset.objects.filter_for_user(user)
            ),
            return_all_if_superuser=False,
        )


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


class DatasetVersionFile(Base):
    uri = models.TextField(null=False, blank=False, unique=True)
    content_type = models.TextField(null=False, blank=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    dataset_version = models.ForeignKey(
        DatasetVersion,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="files",
    )

    objects = DatasetVersionFileManager.from_queryset(DatasetVersionFileQuerySet)()

    @property
    def filename(self):
        return self.uri.split("/")[-1]

    class Meta:
        ordering = ["uri"]


class DatasetLinkQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
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
