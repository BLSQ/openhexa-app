from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.test import SimpleTestCase, override_settings

from hexa.user_management.utils import is_known_password_hash


class IsKnownPasswordHashTest(SimpleTestCase):
    def test_known_hash(self):
        self.assertTrue(is_known_password_hash(make_password("secret")))

    def test_unknown_algorithm(self):
        self.assertFalse(is_known_password_hash("unknown_hasher$1$abc"))

    @override_settings(
        PASSWORD_HASHERS=["django.contrib.auth.hashers.BCryptSHA256PasswordHasher"]
    )
    def test_hasher_library_not_installed(self):
        with patch(
            "django.contrib.auth.hashers.importlib.import_module",
            side_effect=ImportError("No module named 'bcrypt'"),
        ):
            self.assertFalse(
                is_known_password_hash("bcrypt_sha256$$2b$12$abcdefghijklmnopqrstuv")
            )
