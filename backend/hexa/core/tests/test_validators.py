from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from hexa.core.validators import validate_public_slug


class ValidatePublicSlugTest(SimpleTestCase):
    def test_valid(self):
        for value in ["my-dataset-2", "my_dataset", "malaria_2024-v2"]:
            with self.subTest(value=value):
                validate_public_slug(value)

    def test_invalid_format(self):
        for value in [
            "",
            "My-dataset",
            "my dataset",
            "my.dataset",
            "-my",
            "my-",
            "_my",
            "my_",
            "my--ds",
            "my__ds",
            "my-_ds",
            "données",
            "a" * 256,
        ]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError) as ctx:
                    validate_public_slug(value)
                self.assertEqual(ctx.exception.code, "PUBLIC_SLUG_INVALID_FORMAT")

    def test_reserved(self):
        for value in ["new", "api", "admin"]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError) as ctx:
                    validate_public_slug(value)
                self.assertEqual(ctx.exception.code, "PUBLIC_SLUG_RESERVED")

    def test_subdomain_only_words_are_allowed(self):
        for value in ["health", "status", "dhis2", "staging", "metrics"]:
            with self.subTest(value=value):
                validate_public_slug(value)
