from logging import getLogger

from django.core.management.base import BaseCommand

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Set up the Gitea admin user and API token for pipeline versioning"

    def handle(self, *args, **options):
        from hexa.pipelines.gitea import ensure_admin_user

        self.stdout.write("Creating Gitea admin user and API token...")
        try:
            ensure_admin_user()
            self.stdout.write(self.style.SUCCESS("Gitea setup complete. Admin user and API token configured."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Gitea setup failed: {e}"))
            raise
