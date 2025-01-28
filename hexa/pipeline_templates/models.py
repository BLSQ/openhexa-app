import uuid

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from hexa.core.models.base import BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.pipelines.models import Pipeline, PipelineAlreadyExistsError, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class PipelineTemplateQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            Q(workspace__members=user),
            return_all_if_superuser=False,
        )

    def delete(self):
        print("deleting queryset")
        return super().delete()


class PipelineTemplate(SoftDeletedModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "code",
                name="unique_template_code_per_workspace",
                condition=Q(deleted_at__isnull=True),
            ),
            models.UniqueConstraint(
                fields=["name"],
                name="unique_template_name",
                condition=Q(deleted_at__isnull=True),
            ),
        ]
        ordering = ["name"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, default="")
    description = models.TextField(blank=True)
    config = models.JSONField(blank=True, null=True, default=dict)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)

    source_pipeline = models.OneToOneField(
        Pipeline, on_delete=models.SET_NULL, related_name="template", null=True
    )

    objects = DefaultSoftDeletedManager.from_queryset(PipelineTemplateQuerySet)()
    all_objects = IncludeSoftDeletedManager.from_queryset(PipelineTemplateQuerySet)()

    def create_version(self, source_pipeline_version: "PipelineVersion"):
        """Create a new version of the template using a pipeline version as source"""
        template_version = PipelineTemplateVersion.objects.create(
            template=self,
            version_number=self.versions.count() + 1,
            source_pipeline_version=source_pipeline_version,
        )
        return template_version

    def delete(self):
        # Delete references to the source pipeline and version
        if self.source_pipeline:
            source_pipeline = self.source_pipeline
            source_pipeline.template = None
            source_pipeline.save()
        if self.last_version:
            last_version = self.last_version
            last_version.source_pipeline_version = None
            last_version.save()
        return super().delete()

    def upgrade_pipeline(
        self,
        principal: User,
        pipeline: Pipeline,
        template_version: "PipelineTemplateVersion" = None,
    ) -> PipelineVersion:
        """Upgrade a pipeline to the latest version or the specified version of the template"""
        if template_version and template_version.template != self:
            raise ValueError("The specified template version is not for this template")

        template_version = template_version or self.last_version
        return template_version.create_pipeline_version(
            principal, pipeline.workspace, pipeline
        )

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("pipeline_templates.delete_pipeline_template", self):
            raise PermissionDenied
        self.delete()

    @property
    def last_version(self) -> "PipelineTemplateVersion":
        return self.versions.last()

    def __str__(self):
        return self.name


# TODO : popup to ask confirmation
# TODO : can delete permission and hide button for the popup
# TODO : add a test for the BE
@receiver(pre_delete, sender=PipelineTemplate)
def pre_delete_pipeline_template(sender, instance: PipelineTemplate, **kwargs):
    instance.delete()  # When deleting the template from the admin panel, ensure that the references to the source pipeline are also deleted


class PipelineTemplateVersionQuerySet(BaseQuerySet):
    pass


class PipelineTemplateVersion(models.Model):
    class Meta:
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["template", "version_number"],
                name="unique_template_version_number",
            ),
        ]
        indexes = [
            models.Index(
                fields=["template", "version_number"],
                name="index_template_version_number",
            ),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    version_number = models.PositiveIntegerField(editable=False)
    template = models.ForeignKey(
        PipelineTemplate, on_delete=models.CASCADE, related_name="versions"
    )
    source_pipeline_version = models.OneToOneField(
        PipelineVersion,
        on_delete=models.SET_NULL,
        related_name="template_version",
        null=True,
    )

    objects = PipelineTemplateVersionQuerySet.as_manager()

    def _create_pipeline(self, workspace: Workspace) -> Pipeline:
        source_pipeline = self.template.source_pipeline
        if Pipeline.objects.filter(
            workspace=workspace, code=source_pipeline.code
        ).exists():
            raise PipelineAlreadyExistsError(
                f"Failed to create a pipeline with code {source_pipeline.code}, it already exists in the {workspace.name} workspace"
            )
        return Pipeline.objects.create(
            source_template=self.template,
            code=source_pipeline.code,
            name=source_pipeline.name,
            description=self.template.description,
            config=source_pipeline.config,
            workspace=workspace,
        )

    def create_pipeline_version(
        self, principal: User, workspace: Workspace, pipeline=None
    ) -> PipelineVersion:
        pipeline = pipeline or self._create_pipeline(workspace)
        source_version = self.source_pipeline_version
        return PipelineVersion.objects.create(
            source_template_version=self,
            user=principal,
            pipeline=pipeline,
            zipfile=source_version.zipfile,
            parameters=source_version.parameters,
            config=source_version.config,
            timeout=source_version.timeout,
        )

    def __str__(self):
        return f"v{self.version_number} of {self.template.name}"
