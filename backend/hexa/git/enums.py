from enum import StrEnum

from django.db import models


class FileEncoding(models.TextChoices):
    TEXT = "TEXT"
    BASE64 = "BASE64"


class TreeEntryType(StrEnum):
    """Git object types of the entries in a tree listing, named as git names them.
    Only blobs have content to read; submodules (`commit` entries) are skipped.
    """

    BLOB = "blob"  # file
    TREE = "tree"  # directory
