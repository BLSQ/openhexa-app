from datetime import datetime, timezone
from urllib.parse import urlencode

from django.conf import settings
from django.utils.translation import gettext_lazy, override
from django_otp import devices_for_user, user_has_device

from hexa.analytics.api import track
from hexa.core.utils import get_email_attachments, send_mail
from hexa.user_management.models import Organization

USER_DEFAULT_DEVICE_ATTR_NAME = "_default_device"
DEVICE_DEFAULT_NAME = "default"


def default_device(user, confirmed=True):
    """
    confirmed: Pass None to get all devices
    """
    if hasattr(user, USER_DEFAULT_DEVICE_ATTR_NAME):
        return getattr(user, USER_DEFAULT_DEVICE_ATTR_NAME)
    for device in devices_for_user(user, confirmed=confirmed):
        if device.name == DEVICE_DEFAULT_NAME:
            setattr(user, USER_DEFAULT_DEVICE_ATTR_NAME, device)
            return device


def has_configured_two_factor(user):
    return user.is_authenticated and user_has_device(user)


def send_organization_invite(invitation):
    """Send invitation email to organization"""
    title = gettext_lazy(
        f"You've been invited to join the organization {invitation.organization.name} on OpenHEXA"
    )
    token = invitation.generate_invitation_token()
    action_url = f"{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': invitation.email, 'token': token})}"
    invited_by = invitation.invited_by

    with override(invited_by.language):
        send_mail(
            title=title,
            template_name="user_management/mails/invite_organization",
            template_variables={
                "organization": invitation.organization.name,
                "owner": invited_by.display_name,
                "owner_email": invited_by.email,
                "url": action_url,
                "workspace_invitations": invitation.workspace_invitations.all(),
            },
            recipient_list=[invitation.email],
            attachments=get_email_attachments(),
        )

        track(
            request=None,
            event="emails.organization_invite_sent",
            properties={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "organization": invitation.organization.name,
                "invitee_email": invitation.email,
                "invitee_role": invitation.role,
                "status": invitation.status,
            },
        )


def send_organization_add_user_email(
    invited_by, organization: Organization, invitee, role, workspace_invitations=None
):
    """Send email to existing user when added to organization"""
    title = gettext_lazy(
        f"You've been added to the organization {organization.name} on OpenHEXA"
    )
    action_url = f"{settings.NEW_FRONTEND_DOMAIN}/organizations/{organization.id}"

    with override(invitee.language):
        send_mail(
            title=title,
            template_name="user_management/mails/add_existing_user_organization",
            template_variables={
                "organization": organization.name,
                "owner": invited_by.display_name,
                "owner_email": invited_by.email,
                "invitee": invitee.display_name,
                "url": action_url,
                "workspace_invitations": workspace_invitations or [],
            },
            recipient_list=[invitee.email],
            attachments=get_email_attachments(),
        )

        track(
            request=None,
            event="emails.organization_add_user_sent",
            properties={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "organization": organization.name,
                "invitee_email": invitee.email,
                "invitee_role": role,
            },
        )
