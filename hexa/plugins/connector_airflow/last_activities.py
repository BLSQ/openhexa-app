from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from hexa.core.activities import Activity, ActivityList
from hexa.plugins.connector_airflow.models import DAGRun


def get_last_activities(request: HttpRequest):
    activities = [
        Activity(
            description=_(
                f"{run.user.display_name if run.user is not None else _('An unknown user')} launched the <strong>{run.dag.dag_id}</strong> pipeline."
            ),
            occurred_at=run.execution_date,
            status=run.status,
            url=run.get_absolute_url(),
        )
        for run in DAGRun.objects.filter_for_user(request.user)[:5]
    ]

    return ActivityList(activities)
