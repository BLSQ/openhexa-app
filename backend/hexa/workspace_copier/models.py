from django.conf import settings
from django.db import models
from django.utils import timezone
from dpq.models import BaseJob
from oauth2_provider.models import AccessToken

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
    include_connection_secrets = models.BooleanField(default=True)
    same_server = models.BooleanField(default=False)
    # Country codes for a new target workspace; null copies the source's.
    target_countries = models.JSONField(null=True, blank=True)

    # The worker runs after the admin request is gone, so it can only get the
    # tokens from here. They are erased as soon as the run ends.
    source_token = EncryptedTextField(null=True, blank=True)
    target_token = EncryptedTextField(null=True, blank=True)
    # Runs requested from the app have no ServiceAccount token: they act as
    # their requester. The worker issues this token when the run starts, and
    # it is revoked as soon as the run ends.
    acts_as_requester = models.BooleanField(default=False)
    access_token = models.OneToOneField(
        settings.OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="workspace_copy_run",
    )

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    logs = models.TextField(blank=True, default="")
    # Copier name -> StepStatus, written by the reporter as the copy goes.
    steps = models.JSONField(default=dict, blank=True)
    # Everything the requester should act on once the copy is over.
    warnings = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True, default="")
    error = models.TextField(blank=True, default="")
    result_workspace_slug = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # The worker runs one copy at a time for the whole server, so a
            # user queueing several would hold up everyone else's.
            models.UniqueConstraint(
                fields=["created_by"],
                condition=models.Q(
                    acts_as_requester=True,
                    status__in=["QUEUED", "RUNNING"],
                ),
                name="workspace_copy_one_active_run_per_requester",
            )
        ]

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
        # "logs" and "steps" are deliberately left out: the reporter writes them
        # in SQL, and saving this instance's stale copy would erase them.
        self.save(
            update_fields=[
                "status",
                "finished_at",
                "source_token",
                "target_token",
                "summary",
                "warnings",
                "error",
                "result_workspace_slug",
                "updated_at",
            ]
        )
        if self.access_token_id:
            AccessToken.objects.filter(id=self.access_token_id).delete()
            self.access_token = None


def revoke_finished_run_tokens() -> None:
    """Delete the access tokens of every run that is no longer queued or running.

    For runs ended in bulk, like interrupted ones, which never go through
    ``finish()``.
    """
    AccessToken.objects.filter(
        workspace_copy_run__isnull=False,
    ).exclude(
        workspace_copy_run__status__in=[
            WorkspaceCopyRunStatus.QUEUED,
            WorkspaceCopyRunStatus.RUNNING,
        ]
    ).delete()


class WorkspaceCopyJob(BaseJob):
    # Own table so this queue never collides with the other dpq queues.
    class Meta:
        db_table = "workspace_copier_job"
