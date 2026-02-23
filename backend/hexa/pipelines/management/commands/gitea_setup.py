from logging import getLogger

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Verify the Gitea connection and admin user for pipeline versioning"

    def handle(self, *args, **options):
        url = f"{settings.GITEA_URL.rstrip('/')}/api/v1/user"
        self.stdout.write(f"Verifying Gitea connection at {settings.GITEA_URL}...")
        try:
            resp = requests.get(
                url,
                auth=(settings.GITEA_ADMIN_USERNAME, settings.GITEA_ADMIN_PASSWORD),
                timeout=10,
            )
            resp.raise_for_status()
            user = resp.json()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Gitea connection OK. Authenticated as '{user['login']}' (admin={user.get('is_admin', False)})"
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Gitea setup failed: {e}"))
            raise
