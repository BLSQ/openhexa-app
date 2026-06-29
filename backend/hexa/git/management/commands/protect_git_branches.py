from django.core.management.base import BaseCommand

from hexa.git.forgejo import ForgejoAPIError
from hexa.webapps.models import GitWebapp


class Command(BaseCommand):
    help = (
        "Backfill default-branch protection (block force-push and deletion) on "
        "every existing git webapp repository. Idempotent — safe to re-run."
    )

    def handle(self, *args, **options):
        protected = 0
        already_protected = 0
        failed = 0
        for webapp in GitWebapp.objects.select_related("workspace__organization"):
            org, repo = webapp.git_org.slug, webapp.repository
            try:
                webapp.client.protect_branch(org, repo)
            except ForgejoAPIError as e:
                if e.status_code == 409:  # rule already exists
                    already_protected += 1
                    self.stdout.write(f"already protected {org}/{repo}")
                    continue
                failed += 1
                self.stderr.write(self.style.ERROR(f"failed {org}/{repo}: {e}"))
                continue
            protected += 1
            self.stdout.write(f"protected {org}/{repo}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. protected={protected} "
                f"already_protected={already_protected} failed={failed}"
            )
        )
