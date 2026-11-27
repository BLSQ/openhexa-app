from logging import getLogger

from django.db import IntegrityError, transaction
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

from hexa.user_management.models import User
from hexa.workspace_copier.duplicate import (
    CopyAlreadyRunning,
    DuplicateRefused,
    issue_requester_token,
)
from hexa.workspace_copier.models import (
    WorkspaceCopyJob,
    WorkspaceCopyRun,
    WorkspaceCopyRunStatus,
    revoke_finished_run_tokens,
)
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import DatabaseReporter, format_entry
from hexa.workspace_copier.results import CopyResult, format_summary
from hexa.workspace_copier.service import CredentialError, run_copy
from hexa.workspaces.models import Workspace

logger = getLogger(__name__)

INTERRUPTED_MESSAGE = "Interrupted: the worker stopped before this run could finish."

UNEXPECTED_FAILURE_MESSAGE = (
    "The copy failed unexpectedly. Contact your administrator if it keeps failing."
)


def execute_copy_run(run_id: str) -> None:
    """Run one queued workspace copy, recording its outcome on the run.

    Every exception is caught so the run always ends with a final status and
    its tokens erased, whatever happens during the copy.
    """
    try:
        run = WorkspaceCopyRun.objects.select_related("created_by").get(id=run_id)
    except WorkspaceCopyRun.DoesNotExist:
        logger.warning("Workspace copy run %s not found, skipping.", run_id)
        return
    if run.status != WorkspaceCopyRunStatus.QUEUED:
        logger.warning(
            "Workspace copy run %s is %s, not queued; skipping.", run_id, run.status
        )
        return

    reporter = DatabaseReporter(run)
    status = WorkspaceCopyRunStatus.FAILED
    # Created here rather than returned by run_copy, so it survives a copier
    # raising midway: a failed run still records the workspace it created.
    result = CopyResult()
    user_token = None
    try:
        run.mark_running()
        if run.acts_as_requester:
            user_token = issue_requester_token(run)
        run_copy(
            source_url=run.source_url or None,
            source_token=run.source_token or user_token,
            source_slug=run.source_slug,
            target_url=run.target_url or None,
            target_token=run.target_token or user_token,
            target_organization_id=run.target_organization_id or None,
            target_workspace_name=run.target_workspace_name or None,
            target_workspace_slug=run.target_workspace_slug or None,
            resources=set(run.resources),
            options=CopyOptions(
                all_dataset_versions=run.all_dataset_versions,
                include_connection_secrets=run.include_connection_secrets,
                same_server=run.same_server,
                created_by_id=(
                    str(run.created_by_id) if run.acts_as_requester else None
                ),
                target_countries=(
                    tuple(run.target_countries)
                    if run.target_countries is not None
                    else None
                ),
            ),
            reporter=reporter,
            result=result,
        )
        status = (
            WorkspaceCopyRunStatus.SUCCESS_WITH_ERRORS
            if result.has_failures
            else WorkspaceCopyRunStatus.SUCCESS
        )
    except DuplicateRefused as exc:
        reporter.error(str(exc))
        run.error = str(exc)
    except CredentialError as exc:
        for err in exc.errors:
            reporter.error(err)
        run.error = "\n".join(exc.errors)
    except Exception as exc:
        logger.exception("Workspace copy run %s failed", run_id)
        if run.acts_as_requester:
            # Any member can read their own app run, and the exception may name
            # internal hosts or queries: the details stay in the server log.
            run.error = UNEXPECTED_FAILURE_MESSAGE
            reporter.error(run.error)
        else:
            run.error = str(exc)
            reporter.error(f"Copy failed: {exc}")
    finally:
        run.result_workspace_slug = result.workspace_slug or ""
        if result.started_at:
            run.summary = format_summary(result)
            run.warnings = result.all_warnings()
        # A failed log write must not stop finish(), which erases the tokens.
        try:
            reporter.flush()
        except Exception:
            logger.exception("Could not write the final logs of run %s", run_id)
        run.finish(status)


def fail_interrupted_runs() -> int:
    """Mark runs cut off by a previous worker process as failed.

    That is every running run, plus every queued run whose job is gone: the
    AtMostOnceQueue deletes the job when the worker claims it, so a crash
    between claiming and starting would otherwise leave the run queued forever,
    with its tokens stored. Their access tokens are revoked as well.

    Only correct while no other worker is executing runs; the worker command
    guarantees it by holding an advisory lock before calling this.
    """
    now = timezone.now()
    has_job = WorkspaceCopyJob.objects.annotate(
        run_id=KeyTextTransform("run_id", "args")
    ).filter(run_id=Cast(OuterRef("id"), CharField()))
    # One UPDATE statement, so a run and its job committed together by the
    # admin are either both visible to it or both invisible.
    count = WorkspaceCopyRun.objects.filter(
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
    revoke_finished_run_tokens()
    return count


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


def queue_copy_run(
    *,
    created_by: User,
    source_slug: str,
    resources: list[str],
    source_url: str = "",
    source_token: str | None = None,
    target_url: str = "",
    target_token: str | None = None,
    target_organization_id: str = "",
    target_workspace_name: str = "",
    target_workspace_slug: str = "",
    target_countries: list[str] | None = None,
    all_dataset_versions: bool = False,
    include_connection_secrets: bool = True,
    same_server: bool = False,
    acts_as_requester: bool = False,
) -> WorkspaceCopyRun:
    """Create a run and its job, so the worker picks it up."""
    # One transaction: the run and its job exist together or not at all, and
    # the worker is only notified on commit, once the run is readable.
    with transaction.atomic():
        run = WorkspaceCopyRun.objects.create(
            created_by=created_by,
            source_slug=source_slug,
            resources=resources,
            source_url=source_url,
            source_token=source_token,
            target_url=target_url,
            target_token=target_token,
            target_organization_id=target_organization_id,
            target_workspace_name=target_workspace_name,
            target_workspace_slug=target_workspace_slug,
            target_countries=target_countries,
            all_dataset_versions=all_dataset_versions,
            include_connection_secrets=include_connection_secrets,
            same_server=same_server,
            acts_as_requester=acts_as_requester,
        )
        workspace_copy_queue.enqueue("run_workspace_copy", {"run_id": str(run.id)})
    return run


def queue_duplicate_workspace(
    user: User,
    workspace: Workspace,
    *,
    name: str,
    countries: list[str] | None,
    resources: list[str],
    include_connection_secrets: bool,
    all_dataset_versions: bool = False,
) -> WorkspaceCopyRun:
    """Duplicate a workspace into its own organization, acting as ``user``.

    The copy runs as a same-server copy through this server's GraphQL API. Its
    token is issued by the worker when the run starts, not here, so time spent
    queued neither shortens it nor leaves a live token waiting in the database.
    Raises CopyAlreadyRunning if ``user`` already has a copy queued or running.
    """
    try:
        return queue_copy_run(
            created_by=user,
            source_slug=workspace.slug,
            target_organization_id=str(workspace.organization_id),
            target_workspace_name=name,
            target_countries=countries,
            resources=sorted(resources),
            include_connection_secrets=include_connection_secrets,
            all_dataset_versions=all_dataset_versions,
            same_server=True,
            acts_as_requester=True,
        )
    except IntegrityError as exc:
        # The only constraint an insert can break here is one active run per
        # requester; checking it in the database closes the double-click race.
        raise CopyAlreadyRunning from exc
