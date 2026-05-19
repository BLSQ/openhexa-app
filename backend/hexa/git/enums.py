from django.db import models


class FileEncoding(models.TextChoices):
    TEXT = "TEXT"
    BASE64 = "BASE64"
