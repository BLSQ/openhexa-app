import uuid

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Count, Q

from hexa.core.models.base import BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.pipelines.models import Pipeline, PipelineFunctionalType, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class PipelineTemplateQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self.all()

        return self._filter_for_user_and_query_object(
            user,
            Q(workspace__members=user),
            return_all_if_superuser=False,
            return_all_if_organization_admin_or_owner=True,
        )

    def filter_by_tags(self, tags):
        """
        Filter pipeline templates by Tag objects.

        Args:
            tags: QuerySet or list of Tag instances

        Returns
        -------
            Filtered queryset of templates with any of the given tags
        """
        if not tags:
            return self.none()
        return self.filter(tags__in=tags).distinct()

    def with_pipelines_count(self):
        """
        Annotates queryset with the count of active pipelines created from each template.
        Useful for sorting and displaying in GraphQL responses.
        """
        return self.annotate(
            pipelines_count=Count(
                "pipelines",
                filter=Q(pipelines__deleted_at__isnull=True),
                distinct=True,
            )
        )


class PipelineTemplate(SoftDeletedModel):
    UNIQUE_SORT_FIELDS = {"name"}

    @classmethod
    def default_order_by(cls):
        return ["-pipelines_count", "name", "id"]

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
        indexes = [
            models.Index(fields=["name"], name="idx_template_name"),
            models.Index(fields=["functional_type"], name="idx_template_func_type"),
            models.Index(
                fields=["workspace", "functional_type"],
                name="idx_template_ws_func_type",
            ),
        ]
        ordering = ["name"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validated_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the template was validated as official. If set, shows organization name/logo; if null, shows 'Community'.",
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, default="")
    description = models.TextField(blank=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)

    source_pipeline = models.OneToOneField(
        Pipeline, on_delete=models.PROTECT, related_name="template"
    )
    functional_type = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=PipelineFunctionalType.choices,
        help_text="Describes WHAT the template does in data workflows. Optional field used for categorization.",
    )
    tags = models.ManyToManyField(
        "tags.Tag", blank=True, related_name="pipeline_templates"
    )

    objects = DefaultSoftDeletedManager.from_queryset(PipelineTemplateQuerySet)()
    all_objects = IncludeSoftDeletedManager.from_queryset(PipelineTemplateQuerySet)()

    def create_version(
        self,
        source_pipeline_version: PipelineVersion,
        user: User = None,
        changelog: str = None,
    ) -> "PipelineTemplateVersion":
        """Create a new version of the template using a pipeline version as source"""
        return PipelineTemplateVersion.objects.create(
            template=self,
            version_number=self.versions.count() + 1,
            user=user,
            changelog=changelog,
            source_pipeline_version=source_pipeline_version,
        )

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
            pipeline.workspace, principal=principal, pipeline=pipeline
        )

    def new_versions(self, pipeline: Pipeline) -> list["PipelineTemplateVersion"]:
        """Return the versions of the template that are newer than the last version of the pipeline"""
        if pipeline.source_template != self:
            raise ValueError("The specified pipeline is not from this template")

        last_version_from_template = pipeline.versions.filter(
            source_template_version__isnull=False
        ).first()
        if not last_version_from_template:
            return []
        return self.versions.filter(
            created_at__gt=last_version_from_template.created_at
        ).order_by("-created_at")

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("pipeline_templates.delete_pipeline_template", self):
            raise PermissionDenied
        self.delete()

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("pipeline_templates.update_pipeline_template", self):
            raise PermissionDenied
        for key in ["name", "description", "functional_type"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])
        if "tags" in kwargs:
            self.tags.set(kwargs["tags"])
        return self.save()

    @property
    def last_version(self) -> "PipelineTemplateVersion":
        return self.versions.last()

    def __str__(self):
        return self.name


class PipelineTemplateVersionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self.filter(template__in=PipelineTemplate.objects.filter_for_user(user))

    def get_updates_for(self, pipeline: Pipeline):
        """Return the versions of the template that are newer than the last version of the pipeline"""
        if not pipeline.source_template or pipeline.source_template.is_deleted:
            return self.none()

        last_version_created_from_template = pipeline.versions.filter(
            source_template_version__isnull=False
        ).first()

        if not last_version_created_from_template:
            return self.none()

        return self.filter(
            template=pipeline.source_template,
            created_at__gt=last_version_created_from_template.created_at,
        ).order_by("-created_at")


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
    changelog = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    template = models.ForeignKey(
        PipelineTemplate, on_delete=models.CASCADE, related_name="versions"
    )
    source_pipeline_version = models.OneToOneField(
        PipelineVersion, on_delete=models.CASCADE, related_name="template_version"
    )

    objects = PipelineTemplateVersionQuerySet.as_manager()

    def _create_pipeline(self, principal: User, workspace: Workspace) -> Pipeline:
        source_pipeline = self.template.source_pipeline
        data = {
            "source_template": self.template,
            "description": self.template.description,
            "config": source_pipeline.config,
            "functional_type": self.template.functional_type,
        }
        pipeline = Pipeline.objects.create_if_has_perm(
            principal=principal,
            workspace=workspace,
            name=source_pipeline.name or source_pipeline.code,
            **data,
        )
        pipeline.tags.set(self.template.tags.all())
        return pipeline

    def _extract_config(self, pipeline: Pipeline) -> dict:
        """Extract the config from the source pipeline version based on the pipeline config and filter out the parameters with complex types"""
        # Only keep the source parameters with simple types
        kept_source_parameters = [
            param
            for param in self.source_pipeline_version.parameters
            if param.get("type") in {"bool", "int", "str", "float"}
        ]
        kept_param_codes = {p["code"] for p in kept_source_parameters}
        # Keep the config from the previous version
        config_to_keep = pipeline.get_config_from_previous_version(
            kept_source_parameters
        )
        # Use the config from the source pipeline for simple types
        new_version_config = {
            k: v
            for k, v in self.source_pipeline_version.config.items()
            if k in kept_param_codes
        }
        # Keep in priority the config from the previous version
        new_version_config.update(config_to_keep)
        return new_version_config

    def create_pipeline_version(
        self, workspace: Workspace, principal: User = None, pipeline=None
    ) -> PipelineVersion:
        if pipeline is None:
            if principal is None:
                raise ValueError("principal is required when creating a new pipeline")
            pipeline = self._create_pipeline(principal, workspace)

        new_version_config = self._extract_config(pipeline)
        source_version = self.source_pipeline_version

        return PipelineVersion.objects.create(
            source_template_version=self,
            user=principal,
            pipeline=pipeline,
            zipfile=source_version.zipfile,
            parameters=source_version.parameters,
            config=new_version_config,
            timeout=source_version.timeout,
        )

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm(
            "pipeline_templates.delete_pipeline_template_version", self
        ):
            raise PermissionDenied
        self.delete()

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm(
            "pipeline_templates.update_pipeline_template_version", self
        ):
            raise PermissionDenied
        for key in ["changelog"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])
        return self.save()

    @property
    def is_latest_version(self):
        return self == self.template.last_version

    def __str__(self):
        return f"v{self.version_number} of {self.template.name}"
