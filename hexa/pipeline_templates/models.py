import uuid

from django.db import models
from django.db.models import Q

from hexa.core.models.base import BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.workspaces.models import Workspace


class PipelineTemplateQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    pass


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
        Pipeline, on_delete=models.PROTECT, related_name="template"
    )

    objects = DefaultSoftDeletedManager.from_queryset(PipelineTemplateQuerySet)()
    all_objects = IncludeSoftDeletedManager.from_queryset(PipelineTemplateQuerySet)()

    def create_version(self, source_pipeline_version):
        template_version = PipelineTemplateVersion.objects.create(
            template=self,
            version_number=self.versions.count() + 1,
            source_pipeline_version=source_pipeline_version,
        )
        return template_version

    @property
    def last_version(self) -> "PipelineTemplateVersion":
        return self.versions.last()

    def __str__(self):
        return self.name


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
        PipelineVersion, on_delete=models.RESTRICT, related_name="template_version"
    )

    objects = PipelineTemplateVersionQuerySet.as_manager()

    def create_pipeline(self, code, workspace, user):
        source_pipeline = self.template.source_pipeline
        source_version = self.source_pipeline_version
        pipeline = Pipeline.objects.create(
            source_template=self.template,
            code=code,
            name=source_pipeline.name,
            description=self.template.description,
            config=source_pipeline.config,
            workspace=workspace,
        )
        PipelineVersion.objects.create(
            source_template_version=self,
            user=user,
            pipeline=pipeline,
            zipfile=source_version.zipfile,
            parameters=source_version.parameters,
            config=source_version.config,
            timeout=source_version.timeout,
        )
        return pipeline

    def __str__(self):
        return f"v{self.version_number} of {self.template.name}"
