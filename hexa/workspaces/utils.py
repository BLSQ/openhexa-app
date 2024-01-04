from urllib.parse import urlencode

from django.utils.translation import gettext_lazy

from config import settings
from hexa.core.utils import send_mail

from .models import WorkspaceInvitation


def send_workspace_invitation_email(invitation: WorkspaceInvitation):
    token = invitation.generate_invitation_token()
    send_mail(
        title=gettext_lazy(
            f"You've been invited to join the workspace {invitation.workspace.name} on OpenHEXA"
        ),
        template_name="workspaces/mails/invite_external_user",
        template_variables={
            "owner": invitation.invited_by.display_name,
            "workspace_signup_url": f"https://{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': invitation.email, 'token': token})}",
        },
        recipient_list=[invitation.email],
    )
