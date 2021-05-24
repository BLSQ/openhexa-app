from cryptography.fernet import Fernet
from django import test
from django.conf import settings
from django.db import connection

from hexa.core.models.cryptography import EncryptedValue, EncryptedTextField


class ModelsTest(test.TestCase):
    def test_encrypted_value_decrypt_from_encrypted(self):
        value = EncryptedValue(
            encrypted_value=Fernet(settings.ENCRYPTION_KEY).encrypt(b"john123")
        )
        self.assertEqual("john123", value.decrypt())

    def test_encrypted_value_decrypt_from_decrypted(self):
        value = EncryptedValue(decrypted_value="john123")
        self.assertEqual("john123", value.decrypt())

    def test_encrypted_value_as_utf8(self):
        value = EncryptedValue(decrypted_value="john123")
        self.assertIsInstance(value.as_utf8(), str)

    def test_encrypted_value_str(self):
        value = EncryptedValue(decrypted_value="john123")
        self.assertEqual(
            "Encrypted value not displayed for obvious security reason", str(value)
        )

    def test_encrypted_field_get_db_prep_value(self):
        field = EncryptedTextField()
        self.assertIsInstance(
            field.get_db_prep_value(
                EncryptedValue(decrypted_value="john123"), connection=connection
            ),
            str,
        )

    def test_encrypted_field_get_db_prep_value_none(self):
        field = EncryptedTextField()
        self.assertEqual(None, field.get_db_prep_value(None, connection=connection))

    def test_encrypted_field_to_python(self):
        field = EncryptedTextField()
        self.assertEqual(
            EncryptedValue(decrypted_value="john123").decrypt(),
            field.to_python("john123").decrypt(),
        )

    def test_encrypted_field_to_python_none(self):
        field = EncryptedTextField()
        self.assertEqual(None, field.to_python(None))

    def test_encrypted_field_to_python_already_encrypted(self):
        field = EncryptedTextField()
        self.assertEqual(
            EncryptedValue(decrypted_value="john123").decrypt(),
            field.to_python(EncryptedValue(decrypted_value="john123")).decrypt(),
        )

    def test_encrypted_field_from_db_value(self):
        field = EncryptedTextField()
        self.assertEqual(
            EncryptedValue(decrypted_value="john123").decrypt(),
            field.from_db_value(
                EncryptedValue(decrypted_value="john123").as_utf8(),
                expression=None,
                connection=connection,
            ).decrypt(),
        )

    def test_encrypted_field_from_db_value_none(self):
        field = EncryptedTextField()
        self.assertEqual(
            None, field.from_db_value(None, expression=None, connection=connection)
        )
