from django.utils.functional import SimpleLazyObject

from .backends import get_storage_backend
from .backends.base import Storage

storage: Storage = SimpleLazyObject(get_storage_backend)
