import time
import typing
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.core.exceptions import PermissionDenied
from django.core.signing import Signer
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dpq.models import BaseJob

from hexa.core.models import (
    Base,
    BaseIndex,
    BaseIndexableMixin,
    BaseIndexPermission,
    WithStatus,
)
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.behaviors import Status
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembership


class PipelineDoesNotSupportParametersError(Exception):
    pass


class InvalidTimeoutValueError(Exception):
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


class PipelineVersionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(pipeline__in=Pipeline.objects.filter_for_user(user))


class PipelineVersion(models.Model):
    class Meta:
        ordering = ("-number",)

        constraints = [
            models.UniqueConstraint(
                "id",
                "number",
                name="pipeline_unique_version",
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
    number = models.SmallIntegerField()
    zipfile = models.BinaryField()
    parameters = models.JSONField(blank=True, default=dict)
    timeout = models.IntegerField(
        null=True,
        help_text="Time (in seconds) after which the pipeline execution will be stopped (with a default value of 4 hours up to 12 max).",
    )

    objects = PipelineVersionQuerySet.as_manager()

    @property
    def is_schedulable(self):
        return len(self.parameters) == 0 or all(
            [parameter.get("default") is not None for parameter in self.parameters]
        )

    @property
    def display_name(self):
        return f"{self.pipeline.name} - v{self.number}"

    def __str__(self):
        return self.display_name


class PipelineQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user, Q(workspace__members=user), return_all_if_superuser=False
        )


class Pipeline(models.Model):
    class Meta:
        verbose_name = "Pipeline"
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "code",
                name="unique_pipeline_code_per_workspace",
            )
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=200, null=True, blank=True)
    code = models.CharField(max_length=200, default="")
    description = models.TextField(blank=True)
    config = models.JSONField(blank=True, default=dict)
    schedule = models.CharField(max_length=200, null=True, blank=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.SET_NULL, null=True)

    cpu_request = models.CharField(blank=True, max_length=32)
    cpu_limit = models.CharField(blank=True, max_length=32)
    memory_request = models.CharField(blank=True, max_length=32)
    memory_limit = models.CharField(blank=True, max_length=32)
    recipients = models.ManyToManyField(User, through="PipelineRecipient")

    objects = PipelineQuerySet.as_manager()

    def run(
        self,
        user: typing.Optional[User],
        pipeline_version: PipelineVersion,
        trigger_mode: PipelineRunTrigger,
        config: typing.Mapping[typing.Dict, typing.Any] = None,
        send_mail_notifications: bool = False,
    ):
        run = PipelineRun.objects.create(
            user=user,
            pipeline=self,
            pipeline_version=pipeline_version,
            run_id=str(trigger_mode.value) + "__" + str(time.time()),
            trigger_mode=trigger_mode,
            execution_date=timezone.now(),
            state=PipelineRunState.QUEUED,
            config=config if config else self.config,
            access_token=str(uuid.uuid4()),
            send_mail_notifications=send_mail_notifications,
            timeout=pipeline_version.timeout
            if pipeline_version.timeout
            else settings.PIPELINE_RUN_DEFAULT_TIMEOUT,
        )

        return run

    @property
    def last_run(self) -> "PipelineRun":
        return self.pipelinerun_set.first()

    def upload_new_version(self, user: User, zipfile, parameters, timeout: int = None):
        if self.last_version:
            if self.schedule and parameters:
                raise PipelineDoesNotSupportParametersError(
                    "Cannot push a new version with parameters for a scheduled pipeline."
                )
            newnumber = self.last_version.number + 1
        else:
            newnumber = 1

        version = PipelineVersion.objects.create(
            user=user,
            pipeline=self,
            number=newnumber,
            zipfile=zipfile,
            parameters=parameters,
            timeout=timeout,
        )
        return version

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("pipelines.update_pipeline", self):
            raise PermissionDenied

        for key in ["name", "description", "schedule", "config"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        if "recipientIds" in kwargs:
            PipelineRecipient.objects.filter(
                Q(pipeline=self) & ~Q(user_id__in=kwargs["recipientIds"])
            ).delete()
            for member in WorkspaceMembership.objects.filter(
                workspace=self.workspace, user_id__in=kwargs["recipientIds"]
            ):
                PipelineRecipient.objects.get_or_create(user=member.user, pipeline=self)

        return self.save()

    @property
    def last_version(self) -> "PipelineVersion":
        return self.versions.first()

    def get_token(self):
        return Signer().sign_object(
            {
                "id": str(self.id),
                "model": self._meta.model_name,
                "app_label": self._meta.app_label,
            }
        )

    def __str__(self):
        if self.name is not None and self.name != "":
            return self.name

        return self.code


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


class PipelineRunQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(pipeline__in=Pipeline.objects.filter_for_user(user))


class PipelineRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")
    QUEUED = "queued", _("Queued")


class PipelineRun(Base, WithStatus):
    STATUS_MAPPINGS = {
        PipelineRunState.SUCCESS: Status.SUCCESS,
        PipelineRunState.RUNNING: Status.RUNNING,
        PipelineRunState.FAILED: Status.ERROR,
        PipelineRunState.QUEUED: Status.PENDING,
    }

    class Meta:
        ordering = ("-execution_date",)

    user = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    pipeline = models.ForeignKey("Pipeline", on_delete=models.CASCADE)
    pipeline_version = models.ForeignKey("PipelineVersion", on_delete=models.CASCADE)
    run_id = models.CharField(max_length=200, blank=False)
    execution_date = models.DateTimeField()
    last_heartbeat = models.DateTimeField(auto_now_add=True)
    trigger_mode = models.CharField(
        max_length=200, blank=False, choices=PipelineRunTrigger.choices
    )
    state = models.CharField(
        max_length=200, blank=False, choices=PipelineRunState.choices
    )
    duration = models.DurationField(null=True)
    config = models.JSONField(blank=True, default=dict)
    access_token = models.CharField(max_length=200, blank=True)
    messages = models.JSONField(null=True, blank=True, default=list)
    outputs = models.JSONField(null=True, blank=True, default=list)
    run_logs = models.TextField(null=True, blank=True)
    current_progress = models.PositiveSmallIntegerField(default=0)
    send_mail_notifications = models.BooleanField(default=False)
    timeout = models.IntegerField(null=True)

    objects = PipelineRunQuerySet.as_manager()

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.state]
        except KeyError:
            return Status.UNKNOWN

    def get_absolute_url(self) -> str:
        return reverse(
            "pipelines:pipeline_run_detail",
            args=(self.pipeline.id, self.id),
        )

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

    def progress_update(self, percent: int):
        self.refresh_from_db()
        self.current_progress = percent
        self.save()


class EnvironmentsSyncJob(BaseJob):
    # queue table to hold sync job from django-postgres-queue. Need to redefine this class to specify a
    # custom table name, to avoid conflicts with other queue in the system
    class Meta:
        db_table = "catalog_environmentssyncjob"
