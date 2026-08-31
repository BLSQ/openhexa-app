import datetime
import os
from dataclasses import dataclass

from django.conf import settings
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy, override

from hexa.core.utils import send_mail

from .models import (
    PipelineNotificationLevel,
    PipelineRun,
    PipelineRunLogLevel,
    PipelineRunState,
)


def mail_run_recipients(run: PipelineRun):
    workspace_slug = run.pipeline.workspace.slug
    for recipient in run.pipeline.pipelinerecipient_set.all():
        if (
            run.state == PipelineRunState.SUCCESS
            and recipient.notification_level == PipelineNotificationLevel.ERROR
        ):
            continue

        with override(recipient.user.language):
            send_mail(
                title=gettext_lazy("Run report of {code} ({state})").format(
                    code=run.pipeline.code, state=run.state.label
                ),
                template_name="pipelines/mails/run_report",
                template_variables={
                    "pipeline_code": run.pipeline.code,
                    "status": run.state.label,
                    "executed_at": run.execution_date,
                    "duration": (
                        run.duration
                        if run.duration is not None
                        else datetime.timedelta(seconds=0)
                    ),
                    "run_url": f"{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace_slug}/pipelines/{run.pipeline.code}/runs/{run.id}",
                },
                recipient_list=[recipient.user.email],
                attachments=[
                    (
                        "logo_with_text_white.svg",
                        open(
                            os.path.join(
                                settings.BASE_DIR,
                                "hexa/static/img/logo/logo_with_text_white.svg",
                            ),
                            "rb",
                        ).read(),
                        "image/svg+xml",
                    ),
                ],
                fail_without_raising=True,
            )


@dataclass(frozen=True)
class SkipReason:
    priority: str
    reason: str
    advice: str

    @classmethod
    def run_already_in_progress(cls) -> "SkipReason":
        return cls(
            priority=PipelineRunLogLevel.WARNING.name,
            reason=gettext_lazy("A pipeline run is already queued or running"),
            advice=gettext_lazy(
                "The next scheduled execution will proceed as normal if no run is in progress at "
                "that time. If this happens regularly, we advise you to check if your scheduling "
                "interval is configured too tight, or if your pipeline has started to run slower "
                "over time."
            ),
        )

    @classmethod
    def missing_required_parameters(cls, parameters: list[str]) -> "SkipReason":
        return cls(
            priority=PipelineRunLogLevel.ERROR.name,
            reason=format_lazy(
                gettext_lazy("The required parameters {parameters} have no value"),
                parameters=", ".join(parameters),
            ),
            advice=gettext_lazy(
                "The pipeline cannot run unattended until every required parameter has a value. "
                "Set a default value for the missing parameters in the pipeline configuration, "
                "or disable the schedule."
            ),
        )

    @property
    def message(self) -> str:
        """The reason and its advice as a single line, for logs and the run's own messages."""
        return f"Scheduled run skipped. {self.reason} {self.advice}"


def get_skip_reason(pipeline, pipeline_version) -> SkipReason | None:
    """Return why this pipeline cannot start a scheduled run now, or None if it can."""
    # A pipeline may have a schedule but no longer be schedulable, because the parameters or the
    # config of the version to run changed.
    if pipeline.is_schedulable is False:
        return SkipReason.missing_required_parameters(
            pipeline_version.get_missing_required_parameters()
        )

    if PipelineRun.objects.filter(
        pipeline=pipeline,
        state__in=[PipelineRunState.QUEUED, PipelineRunState.RUNNING],
    ).exists():
        return SkipReason.run_already_in_progress()

    return None


def mail_skipped_run_recipients(pipeline, scheduled_time, reason: SkipReason):
    workspace_slug = pipeline.workspace.slug
    for recipient in pipeline.pipelinerecipient_set.all():
        with override(recipient.user.language):
            send_mail(
                title=gettext_lazy("Scheduled run of {code} was skipped").format(
                    code=pipeline.code
                ),
                template_name="pipelines/mails/scheduled_run_skipped",
                template_variables={
                    "pipeline_code": pipeline.code,
                    "scheduled_time": scheduled_time,
                    "reason": reason.reason,
                    "advice": reason.advice,
                    "pipeline_url": f"{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace_slug}/pipelines/{pipeline.code}",
                },
                recipient_list=[recipient.user.email],
                attachments=[
                    (
                        "logo_with_text_white.svg",
                        open(
                            os.path.join(
                                settings.BASE_DIR,
                                "hexa/static/img/logo/logo_with_text_white.svg",
                            ),
                            "rb",
                        ).read(),
                        "image/svg+xml",
                    ),
                ],
                fail_without_raising=True,
            )


def generate_pipeline_container_name(run: PipelineRun) -> str:
    """
    Generate a deterministic Kubernetes-compliant pod name for a pipeline run.

    The name includes workspace, pipeline code, and run ID for readability while
    being deterministic (same run = same name) to allow re-attachment after restarts.

    Format: pipeline-{workspace}-{pipeline-code}-{run-id}
    Kubernetes DNS requirements: lowercase alphanumeric + hyphens, max 63 chars

    Args:
        run: The PipelineRun instance

    Returns
    -------
        A deterministic, Kubernetes-compliant pod name
    """
    run_id = str(run.id)
    max_prefix_length = 63 - 9 - len(run_id) - 2  # "pipeline-", UUID, 2 hyphens
    workspace_max = max_prefix_length // 2
    pipeline_max = max_prefix_length - workspace_max

    # RFC 1123 compliance: must be lowercase alphanumeric with hyphens only
    # - Replace underscores with hyphens (e.g., "get_campaigns" -> "get-campaigns")
    # - Convert to lowercase to ensure compliance
    # - Strip leading/trailing hyphens to meet RFC 1123 requirements
    truncated_workspace_slug = (
        run.pipeline.workspace.slug[:workspace_max].replace("_", "-").lower().strip("-")
    )
    truncated_pipeline_slug = (
        run.pipeline.code[:pipeline_max].replace("_", "-").lower().strip("-")
    )

    return f"pipeline-{truncated_workspace_slug}-{truncated_pipeline_slug}-{run_id}"
