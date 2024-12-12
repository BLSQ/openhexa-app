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


# TODO : model unit test
# TODO : create template test
class TemplateQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    pass


class Template(SoftDeletedModel):
    class Meta:
        verbose_name = "Template"
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "code",
                name="unique_template_code_per_workspace",
                condition=Q(deleted_at__isnull=True),
            )
            # TODO : one title per instance
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200, null=True, blank=True)
    code = models.CharField(max_length=200, default="")
    description = models.TextField(blank=True)
    config = models.JSONField(blank=True, default=dict)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)

    source_pipeline = models.OneToOneField(
        Pipeline, on_delete=models.PROTECT, related_name="template"
    )

    objects = DefaultSoftDeletedManager.from_queryset(TemplateQuerySet)()
    all_objects = IncludeSoftDeletedManager.from_queryset(TemplateQuerySet)()


class TemplateVersionQuerySet(BaseQuerySet):
    pass


class TemplateVersion(models.Model):
    class Meta:
        ordering = ("-created_at",)
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
        Template, on_delete=models.CASCADE, related_name="versions"
    )
    source_pipeline_version = models.OneToOneField(
        PipelineVersion, on_delete=models.RESTRICT, related_name="template_version"
    )

    objects = TemplateVersionQuerySet.as_manager()
