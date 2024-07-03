from django.utils.functional import SimpleLazyObject

from .backends import get_storage_backend
from .backends.base import BaseClient

storage: BaseClient = SimpleLazyObject(get_storage_backend)
