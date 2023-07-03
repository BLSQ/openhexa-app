import datetime

from django.utils.translation import gettext_lazy

from config import settings
from hexa.core.utils import send_mail

from .models import PipelineRun, PipelineRunTrigger


def mail_run_recipients(run: PipelineRun):
    recipient_list = []
    if run.trigger_mode == PipelineRunTrigger.MANUAL:
        recipient_list = [run.user.email]
    else:
        recipient_list = [
            recipient.email for recipient in run.pipeline.recipients.all()
        ]

    workspace_slug = run.pipeline.workspace.slug
    send_mail(
        title=gettext_lazy(f"Run report of {run.pipeline.code} ({run.state.label})"),
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
        recipient_list=recipient_list,
    )
