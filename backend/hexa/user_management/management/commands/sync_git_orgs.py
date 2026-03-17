from django.core.management.base import BaseCommand

from hexa.git.forgejo import ForgejoAPIError, get_forgejo_client
from hexa.user_management.models import Organization


class Command(BaseCommand):
    help = "Creates a Forgejo organization for each existing OpenHEXA organization"

    def handle(self, *args, **options):
        client = get_forgejo_client()
        for org in Organization.objects.all():
            try:
                client.create_organization(org.slug, org.name)
                self.stdout.write(self.style.SUCCESS(f"Created {org.slug}"))
            except ForgejoAPIError as e:
                if e.status_code in (409, 422):
                    self.stdout.write(f"Already exists: {org.slug}")
                else:
                    raise
