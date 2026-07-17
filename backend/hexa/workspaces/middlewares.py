from logging import getLogger

from django.http import HttpRequest

from hexa.workspaces.authentication import WorkspaceToken

logger = getLogger(__name__)


# FIXME: This needs to be changed as it allows the user to query everything with just a simple workspace token.
#        We need to restrict the user's actions to only the workspace he is part of.
def workspace_token_authentication_middleware(get_response):
    """This middleware allows an user to be authenticated through a simple token linked to a workspace"""

    def middleware(request: HttpRequest):
        try:
            auth_type, raw_token = request.headers["Authorization"].split(" ")
        except KeyError:
            return get_response(request)  # No Authorization header
        except ValueError:
            logger.exception("workspace authentication error")
            return get_response(request)

        if auth_type.lower() == "bearer":
            token = WorkspaceToken.authenticate(raw_token)
            if token is not None:
                request.user = token.user
                request.workspace = token.workspace
                request.bypass_two_factor = True

        return get_response(request)

    return middleware
