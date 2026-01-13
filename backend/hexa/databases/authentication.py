from rest_framework import authentication, exceptions

from hexa.workspaces.models import WorkspaceMembership


class WorkspaceTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that supports workspace access tokens.

    Tokens can be passed in the Authorization header as:
    Authorization: Bearer <workspace_access_token>
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            # No authentication provided, return None to allow other auth methods
            return None

        try:
            auth_type, token = auth_header.split(" ", 1)
        except ValueError:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format")

        if auth_type.lower() != "bearer":
            # Not a bearer token, let other auth methods handle it
            return None

        # Try to find workspace membership by access token
        try:
            membership = WorkspaceMembership.objects.select_related("user", "workspace").get(
                access_token=token
            )
            return (membership.user, token)
        except WorkspaceMembership.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid access token")


class WorkspacePermission:
    """
    Permission class to check workspace access for database API.
    """

    def has_permission(self, request, _view):
        # Allow authenticated users
        return request.user and request.user.is_authenticated
