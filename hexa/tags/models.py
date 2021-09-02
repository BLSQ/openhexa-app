from django.db import models

from hexa.core.models import Base


class Tag(Base):
    name = models.TextField()
