from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from hexa.core.validators import validate_public_slug


class ValidatePublicSlugTest(SimpleTestCase):
    def test_valid(self):
        validate_public_slug("my-dataset-2")

    def test_invalid_format(self):
        for value in [
            "",
            "My-dataset",
            "my_dataset",
            "-my",
            "my-",
            "my--ds",
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
