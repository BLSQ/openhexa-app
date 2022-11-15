from datetime import datetime
from logging import getLogger
from time import sleep

from croniter import croniter
from django.core.management.base import BaseCommand
from django.utils import timezone

from hexa.plugins.connector_airflow.models import DAG, Cluster

logger = getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # only run by sequence of 5min
        cutoff = 5 * 60

        while True:
            sequence, start_time = [], timezone.now()
            for cluster in Cluster.objects.all():
                for pipeline in DAG.objects.filter(template__cluster=cluster).exclude(
                    schedule=None
                ):
                    if not croniter.is_valid(pipeline.schedule):
                        logger.warning("pipeline %s invalid schedule", pipeline.id)
                        continue

                    if pipeline.last_run:
                        last_exec = pipeline.last_run.execution_date
                    else:
                        last_exec = timezone.now()

                    cron = croniter(pipeline.schedule, last_exec)
                    next_exec_time = cron.get_next(datetime)
                    next_exec_delay = (next_exec_time - start_time).total_seconds()
                    if next_exec_delay < cutoff:
                        sequence.append((pipeline, next_exec_delay, next_exec_time))

            logger.debug("exec seq %s", sequence)
            for pipeline, delay, exec_time in sorted(sequence, key=lambda e: e[1]):
                # to have a good quality sequence, correct the next delay with an
                # offset based on the diff between NOW and START
                real_delay = delay - (timezone.now() - start_time).total_seconds()
                if real_delay > 0:
                    logger.debug(f"sleep before run: {real_delay}")
                    sleep(real_delay)

                pipeline.run_scheduled()

            empty_delay = cutoff - (timezone.now() - start_time).total_seconds()
            if empty_delay > 0:
                logger.debug("sleep end runs: %s", empty_delay)
                sleep(empty_delay)
