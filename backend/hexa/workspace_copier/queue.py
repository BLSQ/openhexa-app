from logging import getLogger

from django.db.models import (
    CharField,
    Exists,
    F,
    OuterRef,
    Q,
    TextField,
    Value,
)
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast, Concat
from django.utils import timezone
from dpq.queue import AtMostOnceQueue

from hexa.workspace_copier.models import (
    WorkspaceCopyJob,
    WorkspaceCopyRun,
    WorkspaceCopyRunStatus,
)
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import DatabaseReporter, format_entry
from hexa.workspace_copier.results import format_summary
from hexa.workspace_copier.service import CredentialError, run_copy

logger = getLogger(__name__)

INTERRUPTED_MESSAGE = "Interrupted: the worker stopped before this run could finish."


def execute_copy_run(run_id: str) -> None:
    """Run one queued workspace copy, recording its outcome on the run.

    Every exception is caught so the run always ends with a final status and
    its tokens erased, whatever happens during the copy.
    """
    try:
        run = WorkspaceCopyRun.objects.get(id=run_id)
    except WorkspaceCopyRun.DoesNotExist:
        logger.warning("Workspace copy run %s not found, skipping.", run_id)
        return
    if run.status != WorkspaceCopyRunStatus.QUEUED:
        logger.warning(
            "Workspace copy run %s is %s, not queued; skipping.", run_id, run.status
        )
        return

    run.mark_running()
    reporter = DatabaseReporter(run)
    status = WorkspaceCopyRunStatus.FAILED
    try:
        result = run_copy(
            source_url=run.source_url or None,
            source_token=run.source_token,
            source_slug=run.source_slug,
            target_url=run.target_url or None,
            target_token=run.target_token,
            target_organization_id=run.target_organization_id or None,
            target_workspace_name=run.target_workspace_name or None,
            target_workspace_slug=run.target_workspace_slug or None,
            resources=set(run.resources) or None,
            options=CopyOptions(all_dataset_versions=run.all_dataset_versions),
            reporter=reporter,
        )
        run.summary = format_summary(result)
        run.result_workspace_slug = result.workspace_slug or ""
        status = (
            WorkspaceCopyRunStatus.SUCCESS_WITH_ERRORS
            if result.has_failures
            else WorkspaceCopyRunStatus.SUCCESS
        )
    except CredentialError as exc:
        for err in exc.errors:
            reporter.error(err)
        run.error = "\n".join(exc.errors)
    except Exception as exc:
        logger.exception("Workspace copy run %s failed", run_id)
        reporter.error(f"Copy failed: {exc}")
        run.error = str(exc)
    finally:
        reporter.flush()
        run.finish(status)


def fail_interrupted_runs() -> int:
    """Mark runs cut off by a previous worker process as failed.

    That is every running run, plus every queued run whose job is gone: the
    AtMostOnceQueue deletes the job when the worker claims it, so a crash
    between claiming and starting would otherwise leave the run queued forever,
    with its tokens stored.

    Only correct with a single worker replica: at startup, no other worker can
    be executing these runs, so they were cut off by a crash or a restart.
    """
    now = timezone.now()
    has_job = WorkspaceCopyJob.objects.annotate(
        run_id=KeyTextTransform("run_id", "args")
    ).filter(run_id=Cast(OuterRef("id"), CharField()))
    # One UPDATE statement, so a run and its job committed together by the
    # admin are either both visible to it or both invisible.
    return WorkspaceCopyRun.objects.filter(
        Q(status=WorkspaceCopyRunStatus.RUNNING)
        | Q(~Exists(has_job), status=WorkspaceCopyRunStatus.QUEUED)
    ).update(
        status=WorkspaceCopyRunStatus.FAILED,
        error=INTERRUPTED_MESSAGE,
        logs=Concat(
            F("logs"),
            Value(
                f"{format_entry(timezone.localtime(), 'ERROR', INTERRUPTED_MESSAGE)}\n"
            ),
            output_field=TextField(),
        ),
        source_token=None,
        target_token=None,
        finished_at=now,
        updated_at=now,
    )


class WorkspaceCopyQueue(AtMostOnceQueue):
    job_model = WorkspaceCopyJob


# AtMostOnceQueue commits the dequeue before running the task. AtLeastOnceQueue
# would wrap the whole (possibly hours-long) copy in one transaction, hiding
# every log line until the end. A crashed run is not retried automatically.
workspace_copy_queue = WorkspaceCopyQueue(
    tasks={
        "run_workspace_copy": lambda _, job: execute_copy_run(job.args["run_id"]),
    },
    notify_channel="workspace_copy_queue",
)
