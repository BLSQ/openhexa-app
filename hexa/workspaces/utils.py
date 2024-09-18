import secrets
from typing import Optional
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy, override

from hexa.core.utils import send_mail
from hexa.user_management.models import User

from .models import WorkspaceInvitation


def make_random_password(
    length=10, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
):
    return "".join(secrets.choice(allowed_chars) for i in range(length))


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
