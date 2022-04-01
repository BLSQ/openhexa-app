from django.contrib.auth.backends import BaseBackend


class ObjectPermissionBackend(BaseBackend):
    """Custom permission backend that uses model methods to check for permissions."""

    # https://stackoverflow.com/questions/33227521/django-per-object-permission-for-your-own-user-model
