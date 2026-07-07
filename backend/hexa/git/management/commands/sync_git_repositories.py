from django.conf import settings
from django.core.management.base import BaseCommand

from hexa.git.forgejo import ForgejoAPIError, get_forgejo_client
from hexa.webapps.models import GitWebapp

PROXY_USER_EMAIL = "proxy@openhexa.org"


class Command(BaseCommand):
    help = (
        "Ensure the proxy service account exists (password synced to "
        "GIT_PROXY_PASSWORD), then backfill repository configuration on every git "
        "webapp repo: default-branch protection (block force-push and deletion) and "
        "write access for that account. Idempotent — safe to re-run."
    )

    def handle(self, *args, **options):
        if settings.GIT_PROXY_USERNAME:
            if not settings.GIT_PROXY_PASSWORD:
                self.stderr.write(
                    self.style.ERROR(
                        "GIT_PROXY_USERNAME is set but GIT_PROXY_PASSWORD is empty; "
                        "cannot provision the proxy service account."
                    )
                )
                return
            get_forgejo_client().ensure_user(
                settings.GIT_PROXY_USERNAME,
                settings.GIT_PROXY_PASSWORD,
                PROXY_USER_EMAIL,
            )
            self.stdout.write(
                f"Proxy service account '{settings.GIT_PROXY_USERNAME}' is in sync."
            )

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
                    if not e.already_exists:
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
