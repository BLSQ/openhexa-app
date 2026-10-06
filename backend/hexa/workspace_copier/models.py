from django.conf import settings
from django.db import models
from django.utils import timezone
from dpq.models import BaseJob

from hexa.core.models.base import Base
from hexa.core.models.cryptography import EncryptedTextField


class WorkspaceCopyRunStatus(models.TextChoices):
    QUEUED = "QUEUED", "Queued"
    RUNNING = "RUNNING", "Running"
    SUCCESS = "SUCCESS", "Succeeded"
    SUCCESS_WITH_ERRORS = "SUCCESS_WITH_ERRORS", "Succeeded with errors"
    FAILED = "FAILED", "Failed"


class WorkspaceCopyRun(Base):
    """One workspace copy requested from the admin and executed by the worker.

    The dpq job only carries this run's id: dpq deletes its job row as soon as
    the worker claims it, so status, logs and results live here instead.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=32,
        choices=WorkspaceCopyRunStatus.choices,
        default=WorkspaceCopyRunStatus.QUEUED,
    )

    source_url = models.URLField(blank=True)
    source_slug = models.CharField(max_length=255)
    target_url = models.URLField(blank=True)
    target_organization_id = models.CharField(max_length=255, blank=True)
    target_workspace_name = models.CharField(max_length=255, blank=True)
    target_workspace_slug = models.CharField(max_length=255, blank=True)
    resources = models.JSONField(default=list)
    all_dataset_versions = models.BooleanField(default=False)

    # The worker runs after the admin request is gone, so it can only get the
    # tokens from here. They are erased as soon as the run ends.
    source_token = EncryptedTextField(null=True, blank=True)
    target_token = EncryptedTextField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    logs = models.TextField(blank=True, default="")
    summary = models.TextField(blank=True, default="")
    error = models.TextField(blank=True, default="")
    result_workspace_slug = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source_slug} ({self.get_status_display()})"

    @property
    def is_active(self) -> bool:
        return self.status in (
            WorkspaceCopyRunStatus.QUEUED,
            WorkspaceCopyRunStatus.RUNNING,
        )

    def mark_running(self) -> None:
        self.status = WorkspaceCopyRunStatus.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_at"])

    def finish(self, status: str) -> None:
        self.status = status
        self.finished_at = timezone.now()
        self.source_token = None
        self.target_token = None
        # "logs" is deliberately left out: the reporter appends to it in SQL,
        # and saving this instance's stale copy would erase those lines.
        self.save(
            update_fields=[
                "status",
                "finished_at",
                "source_token",
                "target_token",
                "summary",
                "error",
                "result_workspace_slug",
                "updated_at",
            ]
        )


class WorkspaceCopyJob(BaseJob):
    # Own table so this queue never collides with the other dpq queues.
    class Meta:
        db_table = "workspace_copier_job"
