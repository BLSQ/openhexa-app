from django.core.exceptions import ValidationError

from hexa.core.test import TestCase
from hexa.webapps.validators import validate_subdomain


class ValidateSubdomainTest(TestCase):
    def test_valid_subdomains(self):
        for value in ["foo", "my-app", "app123", "123", "a1b", "x" * 63]:
            with self.subTest(value=value):
                validate_subdomain(value)

    def test_rejects_uppercase(self):
        with self.assertRaises(ValidationError):
            validate_subdomain("MyApp")

    def test_rejects_too_short(self):
        for value in ["", "a", "ab"]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validate_subdomain(value)

    def test_rejects_too_long(self):
        with self.assertRaises(ValidationError):
            validate_subdomain("x" * 64)

    def test_rejects_leading_hyphen(self):
        with self.assertRaises(ValidationError):
            validate_subdomain("-abc")

    def test_rejects_trailing_hyphen(self):
        with self.assertRaises(ValidationError):
            validate_subdomain("abc-")

    def test_rejects_underscores(self):
        with self.assertRaises(ValidationError):
            validate_subdomain("my_app")

    def test_rejects_dots(self):
        with self.assertRaises(ValidationError):
            validate_subdomain("my.app")

    def test_rejects_spaces(self):
        with self.assertRaises(ValidationError):
            validate_subdomain("my app")

    def test_rejects_reserved_subdomains(self):
        for value in [
            "www",
            "api",
            "mail",
            "ftp",
            "admin",
            "app",
            "smtp",
            "localhost",
            "wpad",
            "postmaster",
            "sso",
            "staging",
        ]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validate_subdomain(value)

    def test_allows_non_reserved_subdomains(self):
        validate_subdomain("my-api")
        validate_subdomain("admin2")
