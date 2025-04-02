from django.conf import settings
from django.core.management.base import BaseCommand

from hexa.files import storage


class Command(BaseCommand):
    help = "Creates the datasets bucket if it does not exist"

    def handle(self, *args, **options):
        if storage.bucket_exists(settings.WORKSPACE_DATASETS_BUCKET):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Bucket '{settings.WORKSPACE_DATASETS_BUCKET}' already exists"
                )
            )
        else:
            storage.create_bucket(settings.WORKSPACE_DATASETS_BUCKET)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Bucket '{settings.WORKSPACE_DATASETS_BUCKET}' created"
                )
            )
