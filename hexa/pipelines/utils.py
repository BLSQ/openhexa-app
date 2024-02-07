import datetime

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy, override
from slugify import slugify

from hexa.core.utils import send_mail

from .models import PipelineRun, PipelineRunTrigger


def mail_run_recipients(run: PipelineRun):
    recipient_list = []
    if run.trigger_mode == PipelineRunTrigger.MANUAL and run.user is not None:
        recipient_list = [run.user]
    else:
        recipient_list = run.pipeline.recipients.all()

    workspace_slug = run.pipeline.workspace.slug
    for recipient in recipient_list:
        with override(recipient.language):
            send_mail(
                title=gettext_lazy("Run report of {code} ({state})").format(
                    code=run.pipeline.code, state=run.state.label
                ),
                template_name="pipelines/mails/run_report",
                template_variables={
                    "pipeline_code": run.pipeline.code,
                    "status": run.state.label,
                    "executed_at": run.execution_date,
                    "duration": run.duration
                    if run.duration is not None
                    else datetime.timedelta(seconds=0),
                    "run_url": f"https://{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace_slug}/pipelines/{run.pipeline.code}/runs/{run.id}",
                },
                recipient_list=[recipient.email],
            )


def generate_pipeline_container_name(run: PipelineRun) -> str:
    exec_time_str = timezone.now().replace(tzinfo=None, microsecond=0).isoformat()
    suffix = f"-{exec_time_str}-{get_random_string(8)}"
    return slugify(f"pipeline-{run.pipeline.code}"[: 63 - len(suffix)] + suffix)
