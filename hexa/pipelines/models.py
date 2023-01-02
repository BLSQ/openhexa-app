import enum
import time
import typing
import uuid
from datetime import datetime

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex, GistIndex
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
    pipeline = models.ForeignKey("Pipeline", on_delete=models.CASCADE)
    number = models.SmallIntegerField()
    zipfile = models.BinaryField()

    objects = PipelineVersionQuerySet.as_manager()

    @property
    def display_name(self):
        return f"{self.pipeline.name} - v{self.number}"

    def __str__(self):
        return self.display_name


class PipelineQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(user=user),
            return_all_if_superuser=True,
        )


class Pipeline(models.Model):
    class Meta:
        verbose_name = "Pipeline v2"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(unique=True, max_length=200, default="")
    description = models.TextField(blank=True)
    entrypoint = models.CharField(max_length=200, default="")
    parameters = models.JSONField(blank=True, default=dict)
    config = models.CharField(max_length=200, blank=True)
    schedule = models.CharField(max_length=200, null=True, blank=True)

    user = models.ForeignKey(
        "user_management.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    objects = PipelineQuerySet.as_manager()

    def run(
        self,
        user: User,
        pipeline_version: PipelineVersion,
        config: typing.Mapping[str, typing.Any] = None,
    ):

        raw_token, signed_token = self.build_webhook_token()
        #        webhook_path = reverse("pipelines:webhook")

        run = PipelineRun.objects.create(
            user=user,
            pipeline=self,
            pipeline_version=pipeline_version,
            run_id="manual__" + str(time.time()),
            execution_date=timezone.now(),
            state=PipelineRunState.QUEUED,
            config=config if config else self.config,
            webhook_token=raw_token,
        )

        # TODO: Object in DB is created, now we need to really launch k8s/docker
        # need to export "signed_token" as HEXA_WEBHOOK_TOKEN
        # need to export f"{settings.BASE_URL}{webhook_path}" as HEXA_WEBHOOK_URL

        return run

    @property
    def last_run(self) -> "PipelineRun":
        return self.pipelinerun_set.first()

    def upload_new_version(self, user: User, zipfile):
        if self.last_version:
            newnumber = self.last_version.number + 1
        else:
            newnumber = 1

        version = PipelineVersion.objects.create(
            user=user,
            pipeline=self,
            number=newnumber,
            zipfile=zipfile,
        )
        return version

    @property
    def last_version(self) -> "PipelineVersion":
        return self.pipelineversion_set.first()

    @staticmethod
    def build_webhook_token() -> typing.Tuple[str, typing.Any]:
        unsigned = str(uuid.uuid4())

        return unsigned, Signer().sign_object(unsigned)

    def get_token(self):
        return Signer().sign_object(
            {
                "id": str(self.id),
                "model": self._meta.model_name,
                "app_label": self._meta.app_label,
            }
        )


class PipelineRunQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(pipeline__in=Pipeline.objects.filter_for_user(user))


class PipelineRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")
    QUEUED = "queued", _("Queued")


class PipelineRunTrigger(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    MANUAL = "MANUAL"


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
    state = models.CharField(
        max_length=200, blank=False, choices=PipelineRunState.choices
    )
    duration = models.DurationField(null=True)
    config = models.CharField(max_length=200, blank=True)
    webhook_token = models.CharField(max_length=200, blank=True)
    messages = models.JSONField(null=True, blank=True, default=list)
    outputs = models.JSONField(null=True, blank=True, default=list)
    run_logs = models.TextField(null=True, blank=True)
    current_progress = models.PositiveSmallIntegerField(default=0)

    objects = PipelineRunQuerySet.as_manager()

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.state]
        except KeyError:
            return Status.UNKNOWN

    @property
    def trigger_mode(self):
        if self.run_id.startswith("manual"):
            return PipelineRunTrigger.MANUAL
        if self.run_id.startswith("scheduled"):
            return PipelineRunTrigger.SCHEDULED

    def get_absolute_url(self) -> str:
        return reverse(
            "pipelines:pipeline_run_detail",
            args=(self.pipeline.id, self.id),
        )

    def log_message(self, priority: str, message: str):
        self.messages.append(
            {
                "priority": priority if priority else "INFO",
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.save()

    def set_output(self, title: str, uri: str):
        self.outputs.append({"title": title, "uri": uri})
        self.save()

    def progress_update(self, percent: int):
        self.current_progress = percent
        self.save()


class EnvironmentsSyncJob(BaseJob):
    # queue table to hold sync job from django-postgres-queue. Need to redefine this class to specify a
    # custom table name, to avoid conflicts with other queue in the system
    class Meta:
        db_table = "catalog_environmentssyncjob"
