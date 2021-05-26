from cryptography.fernet import Fernet
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = "Generate a random sensitive key"

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            type=str,
            help="The type of key to be created (SECRET_KEY or ENCRYPTION_KEY)",
        )

    def handle(self, *args, **options):
        key_type = options["type"]

        if key_type == "SECRET_KEY":
            self.stdout.write(self.style.SUCCESS(get_random_secret_key()))
        elif key_type == "ENCRYPTION_KEY":
            self.stdout.write(self.style.SUCCESS(Fernet.generate_key().decode("utf-8")))
        else:
            raise CommandError(
                f'Invalid key "{key_type}" - use SECRET_KEY or ENCRYPTION_KEY'
            )
