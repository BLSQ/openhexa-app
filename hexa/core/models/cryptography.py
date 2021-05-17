import typing

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.forms import forms


class EncryptedValue:
    """Value object for the EncryptedField class.
    Uses Fernet symmetric encryption from the cryptography library"""

    def __init__(self, *, encrypted_value: bytes = None, decrypted_value: str = None):
        """Encrypted values can be initialized either from the decrypted value or
        from the already encrypted value"""

        if (encrypted_value is None) == (decrypted_value is None):
            raise ValueError(
                "EncryptedValue constructor expects a single argument (either encrypted_value or decrypted_value"
            )

        if encrypted_value is not None:
            self._encrypted_value = encrypted_value
        elif decrypted_value is not None:
            f = Fernet(settings.ENCRYPTION_KEY)
            self._encrypted_value = f.encrypt(decrypted_value.encode("utf-8"))

    def decrypt(self) -> str:
        """Decrypt the value using the encryption key from the settings"""

        f = Fernet(settings.ENCRYPTION_KEY)

        return f.decrypt(self._encrypted_value).decode("utf-8")

    def as_utf8(self):
        return self._encrypted_value.decode("utf-8")

    def __str__(self):
        return "Encrypted value not displayed for obvious security reason"


class EncryptedField(models.TextField):
    description = "A Fernet-encrypted text field"

    def from_db_value(
        self,
        value: typing.Optional[str],
        expression: typing.Optional[str],
        connection: typing.Any,
    ) -> typing.Optional[EncryptedValue]:
        if value is None:
            return value

        return EncryptedValue(encrypted_value=value.encode("utf-8"))

    def get_db_prep_value(
        self,
        value: typing.Optional[EncryptedValue],
        connection: typing.Any,
        prepared: bool = False,
    ) -> typing.Optional[str]:
        db_prep_value = super().get_db_prep_value(value, connection, prepared)
        if db_prep_value is None:
            return

        return db_prep_value.as_utf8()

    def to_python(
        self, value: typing.Optional[typing.Union[str, EncryptedValue]]
    ) -> typing.Optional[EncryptedValue]:
        if isinstance(value, EncryptedValue):
            return value

        if value is None:
            return value

        return EncryptedValue(decrypted_value=value)

    def formfield(self, **kwargs) -> forms.Field:
        return super().formfield(
            **{
                "type": "password",
            }
        )
