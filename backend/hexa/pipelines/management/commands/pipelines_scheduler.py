from datetime import datetime
from logging import getLogger
from time import sleep

from croniter import croniter
from django.core.management.base import BaseCommand
from django.utils import timezone

from hexa.analytics.api import track
from hexa.pipelines.models import Pipeline, PipelineRunTrigger

logger = getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # only run by sequence of 5min
        cutoff = 5 * 60

        while True:
            sequence, start_time = [], timezone.now()
            for pipeline in Pipeline.objects.exclude(schedule=None):
                if not croniter.is_valid(pipeline.schedule):
                    logger.warning("pipeline %s invalid schedule", pipeline.id)
                    continue
                if pipeline.is_schedulable is False:
                    # A pipeline may have a schedule but not be schedulable because the configuration of the version has changed
                    logger.warning("pipeline %s not schedulable", pipeline.id)
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

                pipeline.run(
                    user=None,
                    pipeline_version=pipeline.last_version,
                    trigger_mode=PipelineRunTrigger.SCHEDULED,
                )
                track(
                    request=None,
                    event="pipelines.pipeline_run",
                    properties={
                        "pipeline_id": pipeline.code,
                        "version_name": (
                            pipeline.last_version.name
                            if pipeline.last_version
                            else None
                        ),
                        "version_id": (
                            str(pipeline.last_version.id)
                            if pipeline.last_version
                            else None
                        ),
                        "trigger": PipelineRunTrigger.SCHEDULED,
                        "workspace": pipeline.workspace.slug,
                    },
                )

            empty_delay = cutoff - (timezone.now() - start_time).total_seconds()
            if empty_delay > 0:
                logger.debug("sleep end runs: %s", empty_delay)
                sleep(empty_delay)
