from collections import Counter
from types import SimpleNamespace

from django.core.management.base import BaseCommand

from hexa.data_studio.models import SavedQuery
from hexa.git.exceptions import GitError

# For queries whose author's account was deleted. `create_repo` reads only
# `display_name` and `email`, and naming the instance beats crediting whoever ran this.
SYSTEM_AUTHOR = SimpleNamespace(display_name="OpenHEXA", email="noreply@openhexa.org")


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
        dry_run = options["dry_run"]
        tally = Counter()

        queryset = SavedQuery.objects.select_related(
            "workspace__organization", "created_by"
        )
        for saved_query in queryset.iterator():
            # Only queries with no repository are touched, so a re-run is free.
            if not saved_query.has_history:
                self._create(saved_query, tally, dry_run)
            elif dry_run:
                # A round trip per query, only worth paying for when nothing is written
                # anyway: the audit of what the run above would have skipped.
                self._report_drift(saved_query, tally)
            else:
                tally["already_created"] += 1

        self._summarise(tally, dry_run)

    def _create(self, saved_query, tally, dry_run):
        if dry_run:
            tally["missing"] += 1
            self.stdout.write(f"no repository: {saved_query.slug}")
            return
        try:
            saved_query.ensure_repo(saved_query.created_by or SYSTEM_AUTHOR)
        except GitError as e:
            tally["failed"] += 1
            self.stderr.write(self.style.ERROR(f"failed {saved_query.slug}: {e}"))
            return
        saved_query.save(update_fields=["repository"])
        tally["created"] += 1
        self.stdout.write(f"created {saved_query.slug} @ {saved_query.repository}")

    def _report_drift(self, saved_query, tally):
        try:
            head = saved_query.get_version_content()
        except GitError as e:
            tally["unreadable"] += 1
            self.stderr.write(self.style.ERROR(f"unreadable {saved_query.slug}: {e}"))
            return
        if head != saved_query.content:
            tally["drifted"] += 1
            self.stdout.write(self.style.WARNING(f"drifted: {saved_query.slug}"))

    def _summarise(self, tally, dry_run):
        if dry_run:
            counts = ("missing", "drifted", "unreadable")
            # Anything reported is work left to do.
            clean = not any(tally[name] for name in counts)
        else:
            counts = ("created", "already_created", "failed")
            # Skipping every query is the expected state of a re-run, not a warning.
            clean = not tally["failed"]

        style = self.style.SUCCESS if clean else self.style.WARNING
        summary = " ".join(f"{name}={tally[name]}" for name in counts)
        self.stdout.write(style(f"{'Checked' if dry_run else 'Done'}. {summary}"))
