from dataclasses import dataclass, fields
from types import SimpleNamespace

from django.core.management.base import BaseCommand

from hexa.data_studio.models import SavedQuery
from hexa.git.exceptions import GitError

# For queries whose author's account was deleted, user is left blank.
# The commit's author used then is the admin account whose credentials
# the app authenticates with.
SYSTEM_AUTHOR = SimpleNamespace(display_name="", email="")


@dataclass
class Backfilled:
    created: int = 0
    already_created: int = 0
    failed: int = 0
    label = "Done"

    @property
    def clean(self) -> bool:
        # Skipping every query is the expected state of a re-run, not a warning.
        return not self.failed


@dataclass
class Audited:
    missing: int = 0
    drifted: int = 0
    unreadable: int = 0
    label = "Checked"

    @property
    def clean(self) -> bool:
        # Anything reported is work left to do.
        return not (self.missing or self.drifted or self.unreadable)


class Command(BaseCommand):
    help = (
        "Create the git repository of every saved query that has none and commit its "
        "current SQL as the first version. Idempotent — safe to re-run. With --dry-run, "
        "writes nothing and reports what it would create, plus the queries whose stored "
        "SQL no longer matches the version recorded for them."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be created, and what has drifted, without writing.",
        )

    def handle(self, *args, **options):
        queryset = SavedQuery.objects.select_related(
            "workspace__organization", "created_by"
        )
        report = (
            self._audit(queryset) if options["dry_run"] else self._backfill(queryset)
        )

        counts = " ".join(f"{f.name}={getattr(report, f.name)}" for f in fields(report))
        style = self.style.SUCCESS if report.clean else self.style.WARNING
        self.stdout.write(style(f"{report.label}. {counts}"))

    def _backfill(self, queryset) -> Backfilled:
        report = Backfilled()
        for saved_query in queryset.iterator():
            # Only queries with no repository are touched, so a re-run is free.
            if saved_query.has_history:
                report.already_created += 1
                continue
            try:
                saved_query.initialize_repository(
                    saved_query.created_by or SYSTEM_AUTHOR
                )
            except GitError as e:
                report.failed += 1
                self.stderr.write(self.style.ERROR(f"failed {saved_query.slug}: {e}"))
                continue
            saved_query.save(update_fields=["repository"])
            report.created += 1
            self.stdout.write(f"created {saved_query.slug} @ {saved_query.repository}")
        return report

    def _audit(self, queryset) -> Audited:
        """Report what a run would create, plus a drift check on the rest.

        The drift check is a round trip per query, only worth paying for when nothing
        is written anyway: the audit of what a real run would have skipped.
        """
        report = Audited()
        for saved_query in queryset.iterator():
            if not saved_query.has_history:
                report.missing += 1
                self.stdout.write(f"no repository: {saved_query.slug}")
                continue
            try:
                head = saved_query.get_version_content()
            except GitError as e:
                report.unreadable += 1
                self.stderr.write(
                    self.style.ERROR(f"unreadable {saved_query.slug}: {e}")
                )
                continue
            if head != saved_query.content:
                report.drifted += 1
                self.stdout.write(self.style.WARNING(f"drifted: {saved_query.slug}"))
        return report
