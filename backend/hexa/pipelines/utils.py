import datetime
import os

from django.conf import settings
from django.utils.translation import gettext_lazy, override

from hexa.core.utils import send_mail

from .models import (
    PipelineNotificationLevel,
    PipelineRun,
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
