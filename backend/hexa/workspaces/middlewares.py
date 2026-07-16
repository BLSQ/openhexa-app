import binascii
from logging import getLogger

from django.core.signing import BadSignature, Signer
from django.http import HttpRequest

from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembership

logger = getLogger(__name__)


# FIXME: This needs to be changed as it allows the user to query everything with just a simple workspace token.
#        We need to restrict the user's actions to only the workspace he is part of.
def workspace_token_authentication_middleware(get_response):
    """This middleware allows an user to be authenticated through a simple token linked to a workspace"""

    def middleware(request: HttpRequest):
        try:
            auth_type, token = request.headers["Authorization"].split(" ")
            if auth_type.lower() == "bearer":
                payload = Signer().unsign_object(token)
                if isinstance(payload, dict):
                    # Identity-scoped token for users with implicit workspace
                    # access (org admins/owners, superusers).
                    user = User.objects.get(id=payload["user_id"])
                    workspace = (
                        Workspace.objects.filter_for_user(user)
                        .filter(id=payload["workspace_id"])
                        .first()
                    )
                    if workspace is not None:
                        request.user = user
                        request.workspace = workspace
                        request.bypass_two_factor = True
                else:
                    membership = WorkspaceMembership.objects.get(access_token=payload)
                    request.user = membership.user
                    request.workspace = membership.workspace
                    request.bypass_two_factor = True
        except KeyError:
            pass  # No Authorization header
        except ValueError:
            logger.exception(
                "workspace authentication error",
            )
        except (UnicodeDecodeError, binascii.Error, BadSignature):
            pass
        except (WorkspaceMembership.DoesNotExist, User.DoesNotExist):
            pass
        return get_response(request)

    return middleware
