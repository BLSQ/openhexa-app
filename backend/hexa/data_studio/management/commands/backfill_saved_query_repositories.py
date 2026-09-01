from types import SimpleNamespace

from django.core.management.base import BaseCommand

from hexa.data_studio.models import SavedQuery
from hexa.git.exceptions import GitError
from hexa.git.forgejo import ForgejoAPIError

# Queries whose author's account was deleted have no user to credit the initial commit
# to. Only `display_name` and `email` are read from it (see GitRepoMixin.create_repo),
# so a stand-in is enough — and naming the instance is more honest than crediting the
# admin who happened to run the command.
SYSTEM_AUTHOR = SimpleNamespace(display_name="OpenHEXA", email="noreply@openhexa.org")


class Command(BaseCommand):
    help = (
        "Create the git repository of every saved query that has none and commit its "
        "current SQL as the first version. Idempotent — safe to re-run. With --check, "
        "records nothing and only reports the queries missing a version and those whose "
        "stored SQL no longer matches the version recorded for it."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="Report what is missing or has drifted without writing anything.",
        )

    def handle(self, *args, **options):
        queryset = SavedQuery.objects.select_related(
            "workspace__organization", "created_by"
        )
        if options["check"]:
            self._check(queryset)
        else:
            self._backfill(queryset)

    def _backfill(self, queryset):
        recorded = 0
        skipped = 0
        failed = 0
        # Only the queries with no version are touched, so a run interrupted halfway
        # picks up where it stopped and a re-run is free.
        for saved_query in queryset.iterator():
            if saved_query.has_history:
                skipped += 1
                continue
            try:
                saved_query.ensure_repo(saved_query.created_by or SYSTEM_AUTHOR)
            except (ForgejoAPIError, GitError) as e:
                failed += 1
                self.stderr.write(self.style.ERROR(f"failed {saved_query.slug}: {e}"))
                continue
            saved_query.save(update_fields=["repository", "last_commit"])
            recorded += 1
            self.stdout.write(
                f"recorded {saved_query.slug} @ {saved_query.last_commit}"
            )

        style = self.style.SUCCESS if not failed else self.style.WARNING
        self.stdout.write(
            style(
                f"Done. recorded={recorded} already_recorded={skipped} failed={failed}"
            )
        )

    def _check(self, queryset):
        missing = 0
        drifted = 0
        unreadable = 0
        for saved_query in queryset.iterator():
            if not saved_query.has_history:
                missing += 1
                self.stdout.write(f"no version: {saved_query.slug}")
                continue
            try:
                head = saved_query.get_version_content()
            except (ForgejoAPIError, GitError) as e:
                unreadable += 1
                self.stderr.write(
                    self.style.ERROR(f"unreadable {saved_query.slug}: {e}")
                )
                continue
            if head != saved_query.content:
                drifted += 1
                self.stdout.write(self.style.WARNING(f"drifted: {saved_query.slug}"))

        style = (
            self.style.SUCCESS
            if not (missing or drifted or unreadable)
            else self.style.WARNING
        )
        self.stdout.write(
            style(
                f"Checked. missing={missing} drifted={drifted} unreadable={unreadable}"
            )
        )
