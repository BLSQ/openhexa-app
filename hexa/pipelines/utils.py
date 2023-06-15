from django.utils.translation import gettext_lazy

from config import settings
from hexa.core.utils import send_mail

from .models import PipelineRun, PipelineRunRecipients, PipelineRunTrigger


def send_mail_to_pipelinerun_users(run: PipelineRun):
    recipient_list = []
    if run.trigger_mode == PipelineRunTrigger.MANUAL:
        recipient_list = [run.user.email]
    else:
        recipient_list = PipelineRunRecipients.objects.get(pipeline=run.pipeline)

    workspace_slug = run.pipeline.workspace.slug
    send_mail(
        title=gettext_lazy(f"Report for pipeline {run.pipeline.code}"),
        template_name="pipelines/mails/run_report",
        template_variables={
            "pipeline_code": run.pipeline.code,
            "status": run.status.name,
            "executed_at": run.execution_date,
            "duration": int(run.duration.total_seconds())
            if run.duration is not None
            else 0,
            "run_url": f"{settings.NEW_FRONTEND_URL}/workspaces/{workspace_slug}/pipelines/{run.pipeline.code}/runs/{run.id}",
        },
        recipient_list=recipient_list,
    )
