from django.db import models
from django.contrib.auth.models import User

from hexa.core.models import Base
from hexa.core.models.cryptography import EncryptedTextField


class Credentials(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE),
    name = models.CharField(max_length=50, null=False),
    value = EncryptedTextField(max_length=100)

    @property
    def route_prefix(self):
        return self.name
