from django.conf import settings
from django.core.management.base import BaseCommand

from hexa.git.forgejo import ForgejoAPIError
from hexa.webapps.models import GitWebapp


class Command(BaseCommand):
    help = (
        "Backfill repository configuration on every git webapp repo: default-branch "
        "protection (block force-push and deletion) and write access for the proxy "
        "service account. Idempotent — safe to re-run."
    )

    def handle(self, *args, **options):
        protected = 0
        already_protected = 0
        granted = 0
        failed = 0
        for webapp in GitWebapp.objects.select_related("workspace__organization"):
            org, repo = webapp.git_org.slug, webapp.repository
            try:
                try:
                    webapp.client.protect_branch(org, repo)
                    protected += 1
                except ForgejoAPIError as e:
                    if e.status_code != 409:  # 409 = rule already exists
                        raise
                    already_protected += 1

                if settings.GIT_PROXY_USERNAME:
                    webapp.client.add_collaborator(
                        org, repo, settings.GIT_PROXY_USERNAME
                    )
                    granted += 1
            except ForgejoAPIError as e:
                failed += 1
                self.stderr.write(self.style.ERROR(f"failed {org}/{repo}: {e}"))
                continue
            self.stdout.write(f"synced {org}/{repo}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. protected={protected} already_protected={already_protected} "
                f"granted={granted} failed={failed}"
            )
        )
