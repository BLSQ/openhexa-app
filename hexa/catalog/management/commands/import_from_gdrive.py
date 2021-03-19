import pandas as pd
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import the content from the Google Drive catalog "prototype"'

    def handle(self, *args, **options):
        self.stdout.write(f"Doing... nothing for now.")
        self.stdout.write(self.style.SUCCESS("Done"))
