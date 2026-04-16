from django.core.exceptions import PermissionDenied


class AuthenticationError(PermissionDenied):
    extensions = {"code": "UNAUTHENTICATED"}
    message = "Resolver requires an authenticated user"
