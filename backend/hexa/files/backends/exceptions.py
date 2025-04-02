from django.core.exceptions import SuspiciousFileOperation


class StorageException(Exception):
    pass


class NotFound(StorageException):
    pass


class AlreadyExists(StorageException):
    pass


__all__ = ["StorageException", "NotFound", "AlreadyExists", "SuspiciousFileOperation"]
