from django_otp import devices_for_user, user_has_device

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


def get_email_attachments():
    """Get standard email attachments including OpenHEXA logo"""
    import os

    from django.conf import settings

    return [
        (
            "logo_with_text_white.png",
            open(
                os.path.join(
                    settings.BASE_DIR, "hexa/static/img/logo/logo_with_text_white.png"
                ),
                "rb",
            ).read(),
            "image/png",
        ),
    ]


def send_organization_invite(invitation):
    """Send invitation email to organization"""
    from datetime import datetime, timezone
    from urllib.parse import urlencode

    from django.conf import settings
    from django.utils.translation import gettext_lazy, override

    from hexa.analytics.api import track
    from hexa.core.utils import send_mail

    title = gettext_lazy(
        f"You've been invited to join the organization {invitation.organization.name} on OpenHEXA"
    )
    token = invitation.generate_invitation_token()
    action_url = f"{settings.NEW_FRONTEND_DOMAIN}/register?{urlencode({'email': invitation.email, 'token': token})}"
    invited_by = invitation.invited_by

    with override(invited_by.language):
        send_mail(
            title=title,
            template_name="user_management/invite_organization",
            template_variables={
                "organization": invitation.organization.name,
                "owner": invited_by.display_name,
                "owner_email": invited_by.email,
                "url": action_url,
                "workspace_invitations": invitation.workspace_invitations,
            },
            recipient_list=[invitation.email],
            attachments=get_email_attachments(),
        )

        track(
            request=None,
            event="emails.organization_invite_sent",
            properties={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "organization": invitation.organization.id,
                "invitee_email": invitation.email,
                "invitee_role": invitation.role,
                "status": invitation.status,
            },
        )
