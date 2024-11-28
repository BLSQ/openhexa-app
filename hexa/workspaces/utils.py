from typing import Optional
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy, override

from hexa.core.utils import send_mail
from hexa.user_management.models import User

from .models import Workspace, WorkspaceInvitation


def send_workspace_invitation_email(
    invitation: WorkspaceInvitation, user: Optional[User] = None
):
    token = invitation.generate_invitation_token()

    with override(user.language if user else invitation.invited_by.language):
        if user:
            title = gettext_lazy(
                f"You've been added to the workspace {invitation.workspace.name}"
            )
            action_url = f"{settings.NEW_FRONTEND_DOMAIN}/user/account"
        else:
            title = gettext_lazy(
                f"You've been invited to join the workspace {invitation.workspace.name} on OpenHEXA"
            )
            action_url = f"{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': invitation.email, 'token': token})}"

        send_mail(
            title=title,
            template_name="workspaces/mails/invite_user",
            template_variables={
                "workspace": invitation.workspace.name,
                "owner": invitation.invited_by.display_name,
                "user": user,
                "url": action_url,
            },
            recipient_list=[invitation.email],
        )


def send_workspace_insertion_email(workspace: Workspace, owner: User, user: User):
    with override(user.language):
        title = gettext_lazy(
            f"You've been added to the workspace {workspace.name} on OpenHEXA"
        )
        action_url = f"{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace.slug}"
        variables = {
            "workspace": workspace.name,
            "owner": owner.display_name,
            "user": user,
            "url": action_url,
        }

        send_mail(
            title=title,
            template_name="workspaces/mails/insert_user",
            template_variables=variables,
            recipient_list=[user.email],
        )
