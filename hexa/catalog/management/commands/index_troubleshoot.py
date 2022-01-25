from logging import getLogger

from django.core.management.base import BaseCommand

from hexa.catalog.models import Index

logger = getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexes = Index.objects.all().iterator(chunk_size=50)

        for index in indexes:
            if index.object is None:
                created_at = index.created_at.strftime("%d/%m/%y")
                updated_at = index.updated_at.strftime("%d/%m/%y")
                logger.warning(
                    f"Orphan: Index {index.id} ({created_at}, {updated_at}) for CT {index.content_type.name}"
                )
