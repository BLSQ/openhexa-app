from django.db.models.signals import post_save
from django.dispatch import receiver

from hexa.plugins.connector_accessmod.models import Analysis
from hexa.plugins.connector_airflow.models import DAGRun, DAGRunState


@receiver(post_save, sender=DAGRun, dispatch_uid="my_unique_identifier")
def update_analysis_handler(sender: type, *, instance: DAGRun, **kwargs):
    if instance.state in [DAGRunState.RUNNING, DAGRunState.FAILED, DAGRunState.SUCCESS]:
        try:
            analysis = Analysis.objects.get(dag_run=instance)
            analysis.update_status_from_dag_run_state(instance.state)
        except Analysis.DoesNotExist:
            pass
