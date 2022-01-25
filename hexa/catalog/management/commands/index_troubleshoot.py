from logging import getLogger

from django.core.management.base import BaseCommand

from hexa.catalog.models import Index

logger = getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexes = Index.objects.all().iterator(chunk_size=50)
        orphan_count = 0

        for index in indexes:
            if index.object is None:
                orphan_count += 1
                created_at = index.created_at.strftime("%d/%m/%y")
                updated_at = index.updated_at.strftime("%d/%m/%y")
                self.stdout.write(
                    self.style.WARNING(
                        f"Orphan: Index {index.id} ({created_at}, {updated_at}) for CT {index.content_type.name}"
                    )
                )

        if orphan_count == 0:
            self.stdout.write(self.style.SUCCESS("No orphaned index found"))
        else:
            self.stdout.write(
                self.style.WARNING(f"Found {orphan_count} orphaned indexes")
            )
