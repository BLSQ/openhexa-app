from django.core.validators import RegexValidator
from django.db import models

from hexa.core.models import Base
from hexa.core.models.cryptography import EncryptedTextField


class Credentials(Base):
    user = models.ForeignKey("user_management.User", on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50,
        null=False,
        validators=[
            RegexValidator(
                regex="^[a-zA-Z]*$", message="name must be composed of letters only "
            )
        ],
    )
    value = EncryptedTextField(
        max_length=100,
        validators=[
            RegexValidator(
                regex="^[a-zA-Z0-9]*$", message="value must be alphanumeric "
            )
        ],
    )

    @property
    def route_prefix(self):
        return self.name
