import base64
import secrets
import time
import typing
import uuid
from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.core.exceptions import PermissionDenied
from django.core.signing import Signer, TimestampSigner
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dpq.models import BaseJob
from slugify import slugify

from hexa.core.models import (
    Base,
    BaseIndex,
    BaseIndexableMixin,
    BaseIndexPermission,
    WithStatus,
)
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.behaviors import Status
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.pipelines.constants import UNIQUE_PIPELINE_VERSION_NAME
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class PipelineAlreadyExistsError(Exception):
    pass


class PipelineDoesNotSupportParametersError(Exception):
    pass


class InvalidTimeoutValueError(Exception):
    pass


class MissingPipelineConfiguration(Exception):
    """The pipeline configuration is missing. This exception should be raised when trying to schedule a pipeline without a configuration for the required parameters."""

    pass


class Index(BaseIndex):
    class Meta:
        verbose_name = "Pipeline index"
        verbose_name_plural = "Pipeline indexes"
        ordering = ("external_name",)
        indexes = [
            GinIndex(
                name="pipeline_index_search_gin_idx",
                fields=["search"],
                opclasses=["gin_trgm_ops"],
            ),
            GistIndex(
                name="pipeline_index_search_gist_idx",
                fields=["search"],
                opclasses=["gist_trgm_ops"],
            ),
        ]


class IndexPermission(BaseIndexPermission):
    index = models.ForeignKey("Index", on_delete=models.CASCADE)


class IndexableMixin(BaseIndexableMixin):
    def get_permission_model(self):
        return IndexPermission

    def get_index_model(self):
        return Index


class Environment(IndexableMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    auto_sync = models.BooleanField(default=True)

    indexes = GenericRelation("pipelines.Index")

    objects = BaseQuerySet.as_manager()

    class Meta:
        abstract = True

    def sync(self):
        raise NotImplementedError


class PipelineRunTrigger(models.TextChoices):
    SCHEDULED = "scheduled", _("Scheduled")
    MANUAL = "manual", _("Manual")
    WEBHOOK = "webhook", _("Webhook")


class PipelineVersionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self.filter(pipeline__in=Pipeline.objects.filter_for_user(user))


class PipelineVersion(models.Model):
    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["pipeline", "name"], name=UNIQUE_PIPELINE_VERSION_NAME
            ),
            models.UniqueConstraint(
                fields=["pipeline", "version_number"],
                name="unique_pipeline_version_number",
            ),
        ]
        indexes = [
            models.Index(
                fields=["pipeline", "version_number"],
                name="index_pipeline_version_number",
            ),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    pipeline = models.ForeignKey(
        "Pipeline", on_delete=models.CASCADE, related_name="versions"
    )
    version_number = models.PositiveIntegerField(editable=False)
    name = models.CharField(max_length=250, null=True, blank=True)
    external_link = models.URLField(blank=True, null=True)
    description = models.TextField(null=True)
    zipfile = models.BinaryField(null=True)
    parameters = models.JSONField(blank=True, default=dict)
    config = models.JSONField(blank=True, default=dict)

    timeout = models.IntegerField(
        null=True,
        help_text="Time (in seconds) after which the pipeline execution will be stopped (with a default value of 4 hours up to 12 max).",
    )

    source_template_version = models.ForeignKey(
        "pipeline_templates.PipelineTemplateVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pipeline_versions",
    )

    objects = PipelineVersionQuerySet.as_manager()

    def _increment_version_number(self):
        with transaction.atomic():
            previous_version = (
                PipelineVersion.objects.filter(pipeline=self.pipeline)
                .order_by("-version_number")
                .first()
            )
            self.version_number = (
                (previous_version.version_number + 1) if previous_version else 1
            )

    def save(self, *args, **kwargs):
        if not self.version_number:  # Increment for new records only
            self._increment_version_number()
        super().save(*args, **kwargs)

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("pipelines.update_pipeline_version", self):
            raise PermissionDenied

        if kwargs.get("config") and self.pipeline.schedule:
            self.validate_new_config(kwargs.get("config"))

        for key in ["name", "description", "external_link", "config"]:
            if key in kwargs and kwargs[key] is not None:
                setattr(self, key, kwargs[key])

        return self.save()

    def validate_new_config(self, new_config: dict):
        for parameter in self.parameters:
            if (
                parameter.get("required")
                and parameter.get("default") is None
                and self.config.get(parameter.get("code"))
            ) and new_config.get(parameter.get("code")) is None:
                raise PipelineDoesNotSupportParametersError(
                    "Cannot push an unschedulable new version for a scheduled pipeline."
                )

    @property
    def is_schedulable(self):
        return all(
            parameter.get("required") is False
            or parameter.get("default") is not None
            or self.config.get(parameter["code"]) is not None
            for parameter in self.parameters
        )

    @property
    def is_latest_version(self):
        return self == self.pipeline.last_version

    @property
    def version_name(self):
        if self.name:
            return self.name + f" [v{self.version_number}]"
        return f"v{self.version_number}"

    @property
    def display_name(self):
        return f"{self.pipeline.name} - {self.version_name}"

    def __str__(self):
        return self.display_name


class PipelineQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self._filter_for_user_and_query_object(
            user,
            Q(workspace__members=user),
            return_all_if_superuser=False,
        )


class PipelineType(models.TextChoices):
    NOTEBOOK = "notebook", _("Notebook")
    ZIPFILE = "zipFile", _("ZipFile")


class PipelineRunLogLevel(models.IntegerChoices):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    @classmethod
    def parse_log_level(cls, value):
        if isinstance(value, int) and 0 <= value <= 4:
            return value
        if isinstance(value, str):
            if value.isdigit():
                return cls.parse_log_level(int(value))
            value = value.upper()
            if hasattr(cls, value):
                return getattr(cls, value)
        return cls.INFO


class PipelineManager(DefaultSoftDeletedManager.from_queryset(PipelineQuerySet)):
    def _create_unique_code(self, name: str, workspace: Workspace):
        suffix = ""
        while True:
            code = slugify(name[: 255 - len(suffix)] + suffix)
            if not super().filter(workspace=workspace, code=code).exists():
                return code
            suffix = "-" + secrets.token_hex(3)

    def create_if_has_perm(
        self, principal: User, workspace: Workspace, name: str, **kwargs
    ):
        if not principal.has_perm("pipelines.create_pipeline", workspace):
            raise PermissionDenied
        if kwargs.get("code"):
            raise ValueError("The code field is automatically generated.")
        code = self._create_unique_code(name, workspace)
        return super().create(name=name, workspace=workspace, code=code, **kwargs)


class Pipeline(SoftDeletedModel):
    class Meta:
        verbose_name = "Pipeline"
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "code",
                name="unique_pipeline_code_per_workspace",
                condition=Q(deleted_at__isnull=True),
                violation_error_message="A pipeline with the same code already exists in this workspace. Consider using `create_if_has_perm` method.",
            )
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200, null=True, blank=True)
    code = models.CharField(
        max_length=200, default=""
    )  # this is the auto-generated unique identifier for the pipeline, TODO: rename it to slug
    description = models.TextField(blank=True)
    config = models.JSONField(blank=True, default=dict)
    schedule = models.CharField(max_length=200, null=True, blank=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)
    webhook_enabled = models.BooleanField(default=False)

    cpu_request = models.CharField(blank=True, max_length=32)
    cpu_limit = models.CharField(blank=True, max_length=32)
    memory_request = models.CharField(blank=True, max_length=32)
    memory_limit = models.CharField(blank=True, max_length=32)
    recipients = models.ManyToManyField(User, through="PipelineRecipient")
    webhook_token = models.TextField(null=True, blank=True)

    type = models.CharField(
        max_length=200,
        blank=False,
        choices=PipelineType.choices,
        default=PipelineType.ZIPFILE,
    )
    notebook_path = models.TextField(null=True, blank=True)
    source_template = models.ForeignKey(
        "pipeline_templates.PipelineTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pipelines",
    )

    objects = PipelineManager()
    all_objects = IncludeSoftDeletedManager.from_queryset(PipelineQuerySet)()

    def run(
        self,
        user: typing.Optional[User],
        pipeline_version: PipelineVersion,
        trigger_mode: PipelineRunTrigger,
        config: typing.Mapping[typing.Dict, typing.Any] | None = None,
        send_mail_notifications: bool = True,
        log_level: PipelineRunLogLevel = PipelineRunLogLevel.INFO,
    ):
        timeout = settings.PIPELINE_RUN_DEFAULT_TIMEOUT
        if pipeline_version and pipeline_version.timeout:
            timeout = pipeline_version.timeout
        run = PipelineRun.objects.create(
            user=user,
            pipeline=self,
            pipeline_version=pipeline_version,
            run_id=str(trigger_mode.value) + "__" + str(time.time()),
            trigger_mode=trigger_mode,
            execution_date=timezone.now(),
            state=PipelineRunState.QUEUED,
            config=(
                self.merge_pipeline_config(config, pipeline_version.config)
                if pipeline_version
                else self.config
            ),
            access_token=str(uuid.uuid4()),
            send_mail_notifications=send_mail_notifications,
            timeout=timeout,
            log_level=log_level,
        )

        return run

    @property
    def last_run(self) -> "PipelineRun":
        return self.pipelinerun_set.first()

    @property
    def is_schedulable(self):
        if self.type == PipelineType.NOTEBOOK:
            return True
        elif self.type == PipelineType.ZIPFILE:
            return self.last_version and self.last_version.is_schedulable

    def get_config_from_previous_version(self, new_parameters: list[dict]):
        """
        Get the config from the previous version of the pipeline considering only overlapping parameters between the new and the previous version.
        """

        def remove_default(parameter):
            parameter_without_default = parameter.copy()
            if "default" in parameter:
                del parameter_without_default["default"]
            return parameter_without_default

        previous_config_from_overlapping_parameters = {}
        if self.last_version:
            previous_parameters = list(
                map(remove_default, self.last_version.parameters)
            )
            overlapping_parameters = [
                new_parameter
                for new_parameter in new_parameters
                if remove_default(new_parameter) in previous_parameters
            ]
            previous_config_from_overlapping_parameters = {
                overlapping_parameter["code"]: value
                for overlapping_parameter in overlapping_parameters
                if (
                    value := self.last_version.config.get(
                        overlapping_parameter["code"],
                        overlapping_parameter.get("default"),
                    )
                )
                is not None
            }
        return {
            new_parameter["code"]: value
            for new_parameter in new_parameters
            if (
                value := previous_config_from_overlapping_parameters.get(
                    new_parameter["code"], new_parameter.get("default")
                )
            )
            is not None
        }

    def upload_new_version(
        self,
        user: User,
        parameters: list[dict],
        name: str,
        zipfile: str = None,
        description: str = None,
        config: typing.Mapping[typing.Dict, typing.Any] | None = None,
        external_link: str = None,
        timeout: int = None,
    ):
        if not user.has_perm("pipelines.update_pipeline", self):
            raise PermissionDenied

        config = config or self.get_config_from_previous_version(parameters)

        version = PipelineVersion(
            user=user,
            pipeline=self,
            name=name,
            description=description,
            external_link=external_link,
            zipfile=zipfile,
            config=config,
            parameters=parameters,
            timeout=timeout,
        )

        if self.last_version and self.schedule and not version.is_schedulable:
            raise PipelineDoesNotSupportParametersError(
                "Cannot push an unschedulable new version for a scheduled pipeline."
            )
        version.save()
        return version

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("pipelines.update_pipeline", self):
            raise PermissionDenied
        if (
            self.last_version
            and self.last_version.is_schedulable is False
            and not self.schedule
            and kwargs.get("schedule")
        ):
            raise MissingPipelineConfiguration

        for key in ["name", "description", "schedule", "config"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        if "webhook_enabled" in kwargs:
            self.set_webhook_state(kwargs["webhook_enabled"])

        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("pipelines.delete_pipeline", self):
            raise PermissionDenied

        if PipelineRun.objects.filter(
            pipeline=self, state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING]
        ).exists():
            raise PermissionDenied

        self.delete()

    @property
    def last_version(self) -> "PipelineVersion":
        return self.versions.first()

    @property
    def has_new_template_versions(self):
        PipelineTemplateVersion = apps.get_model(
            "pipeline_templates", "PipelineTemplateVersion"
        )
        return PipelineTemplateVersion.objects.get_updates_for(self).exists()

    def get_token(self):
        return Signer().sign_object(
            {
                "id": str(self.id),
                "model": self._meta.model_name,
                "app_label": self._meta.app_label,
            }
        )

    def set_webhook_state(self, enabled: bool):
        if enabled:
            self.generate_webhook_token()

        self.webhook_enabled = enabled

    def generate_webhook_token(self):
        signer = TimestampSigner()
        self.webhook_token = base64.b64encode(
            signer.sign(self.id).encode("utf-8")
        ).decode()
        self.save()

    def merge_pipeline_config(
        self,
        provided_config: typing.Mapping[typing.Dict, typing.Any] | None,
        pipeline_version_config: typing.Mapping[typing.Dict, typing.Any],
    ):
        if provided_config is None:
            return pipeline_version_config

        cleaned_provided_config = {
            key: value for key, value in provided_config.items() if value is not None
        }
        cleaned_pipeline_version_config = {
            key: value
            for key, value in pipeline_version_config.items()
            if value is not None
        }
        merged_config = {**cleaned_pipeline_version_config, **cleaned_provided_config}
        return merged_config

    def get_or_create_template(self, name: str, code: str, description: str):
        if not hasattr(self, "template"):
            PipelineTemplate = apps.get_model("pipeline_templates", "PipelineTemplate")
            self.template = PipelineTemplate.objects.create(
                name=name,
                code=code,
                description=description,
                workspace=self.workspace,
                source_pipeline=self,
            )
            return self.template, True
        if self.template.is_deleted:
            self.template.restore()
            self.template.name = name
            self.template.code = code
            self.template.description = description
            self.template.save()
        return self.template, False

    def __str__(self):
        if self.name is not None and self.name != "":
            return self.name

        return self.code


class PipelineNotificationLevel(models.TextChoices):
    ALL = "ALL", _("All")
    ERROR = "ERROR", _("Error")


class PipelineRecipientManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        pipeline: Pipeline,
        user: User,
        level: PipelineNotificationLevel,
    ):
        if not principal.has_perm("pipelines.update_pipeline", pipeline):
            raise PermissionDenied

        return self.create(pipeline=pipeline, user=user, notification_level=level)


class PipelineRecipient(Base):
    class Meta:
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(
                "user",
                "pipeline",
                name="unique_recipient_per_pipeline",
            )
        ]

    user = models.ForeignKey(
        "user_management.User", null=False, on_delete=models.CASCADE
    )
    pipeline = models.ForeignKey(Pipeline, null=False, on_delete=models.CASCADE)
    notification_level = models.CharField(
        max_length=200,
        blank=False,
        default=PipelineNotificationLevel.ALL,
        choices=PipelineNotificationLevel.choices,
    )
    objects = PipelineRecipientManager()

    def update_if_has_perm(self, *, principal: User, level: PipelineNotificationLevel):
        if not principal.has_perm("pipelines.update_pipeline", self.pipeline):
            raise PermissionDenied

        self.notification_level = level
        return self.save()

    def delete_if_has_perm(self, *, principal: User):
        if not principal.has_perm("pipelines.update_pipeline", self.pipeline):
            raise PermissionDenied

        return self.delete()


class PipelineRunQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        return self.filter(pipeline__in=Pipeline.objects.filter_for_user(user))


class PipelineRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")
    QUEUED = "queued", _("Queued")
    TERMINATING = "terminating", _("terminating")
    STOPPED = "stopped", _("Stopped")


class PipelineRun(Base, WithStatus):
    STATUS_MAPPINGS = {
        PipelineRunState.SUCCESS: Status.SUCCESS,
        PipelineRunState.RUNNING: Status.RUNNING,
        PipelineRunState.FAILED: Status.ERROR,
        PipelineRunState.QUEUED: Status.PENDING,
        PipelineRunState.STOPPED: Status.STOPPED,
        PipelineRunState.TERMINATING: Status.TERMINATING,
    }

    class Meta:
        ordering = ("-execution_date",)
        indexes = [
            models.Index(fields=["access_token"]),
        ]

    user = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    pipeline = models.ForeignKey("Pipeline", on_delete=models.CASCADE)
    pipeline_version = models.ForeignKey(
        "PipelineVersion", null=True, on_delete=models.CASCADE
    )
    run_id = models.CharField(max_length=200, blank=False)
    execution_date = models.DateTimeField()
    last_heartbeat = models.DateTimeField(auto_now_add=True)
    trigger_mode = models.CharField(
        max_length=200, blank=False, choices=PipelineRunTrigger.choices
    )
    state = models.CharField(
        max_length=200, blank=False, choices=PipelineRunState.choices
    )
    duration = models.DurationField(null=True, blank=True)
    config = models.JSONField(blank=True, default=dict)
    access_token = models.CharField(max_length=200, blank=True)
    messages = models.JSONField(null=True, blank=True, default=list)
    outputs = models.JSONField(null=True, blank=True, default=list)
    run_logs = models.TextField(null=True, blank=True)
    current_progress = models.PositiveSmallIntegerField(default=0)
    timeout = models.IntegerField(null=True)
    send_mail_notifications = models.BooleanField(default=True)
    stopped_by = models.ForeignKey(
        "user_management.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    log_level = models.IntegerField(
        choices=PipelineRunLogLevel.choices, default=PipelineRunLogLevel.INFO
    )
    objects = PipelineRunQuerySet.as_manager()

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.state]
        except KeyError:
            return Status.UNKNOWN

    def get_code(self):
        return self.pipeline_version.zipfile

    def log_message(self, priority: str, message: str):
        self.refresh_from_db()
        if self.messages is None:
            self.messages = []
        self.messages.append(
            {
                "priority": priority if priority else "INFO",
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.save()

    def add_output(self, uri: str, output_type: str, name: typing.Optional[str]):
        self.refresh_from_db()
        if self.outputs is None:
            self.outputs = []
        self.outputs.append(
            {
                "uri": uri,
                "name": name,
                "type": output_type,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.save()

    def stop(self, principal: User):
        if not principal.has_perm("pipelines.stop_pipeline", self.pipeline):
            raise PermissionDenied

        self.state = PipelineRunState.TERMINATING
        self.stopped_by = principal
        self.save()

    def progress_update(self, percent: int):
        self.refresh_from_db()
        self.current_progress = percent
        self.save()


class EnvironmentsSyncJob(BaseJob):
    # queue table to hold sync job from django-postgres-queue. Need to redefine this class to specify a
    # custom table name, to avoid conflicts with other queue in the system
    class Meta:
        db_table = "catalog_environmentssyncjob"
