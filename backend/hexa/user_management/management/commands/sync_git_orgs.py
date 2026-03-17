from django.conf import settings
from django.core.management.base import BaseCommand

from hexa.git.forgejo import ForgejoAPIError, ForgejoClient
from hexa.user_management.models import Organization


class Command(BaseCommand):
    help = "Creates a Forgejo organization for each existing OpenHEXA organization"

    def handle(self, *args, **options):
        client = ForgejoClient(
            url=settings.GIT_SERVER_URL,
            username=settings.GIT_SERVER_ADMIN_USERNAME,
            password=settings.GIT_SERVER_ADMIN_PASSWORD,
            application_name="openhexa-sync-git-orgs-command",
        )
        for org in Organization.objects.all():
            try:
                client.create_organization(org.slug, org.name)
                self.stdout.write(self.style.SUCCESS(f"Created {org.slug}"))
            except ForgejoAPIError as e:
                if e.status_code in (409, 422):
                    self.stdout.write(f"Already exists: {org.slug}")
                else:
                    raise
