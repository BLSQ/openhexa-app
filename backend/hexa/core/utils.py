import base64
import os
import typing
from email.mime.image import MIMEImage
from logging import getLogger

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from mjml import mjml2html

from hexa.core.models import FailedEmail

logger = getLogger(__name__)


def get_email_attachments():
    """Get standard email attachments including OpenHEXA logo"""
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


def build_email(
    *,
    title: str,
    recipient_list: typing.Sequence[str],
    text_message: str,
    html_message: str = None,
    attachments: typing.Sequence[typing.Tuple[str, bytes, str]] = None,
) -> EmailMultiAlternatives:
    mail = EmailMultiAlternatives(
        subject=title,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    if html_message:
        mail.attach_alternative(html_message, "text/html")

    if attachments:
        for filename, content, mimetype in attachments:
            if mimetype.startswith("image/") and not mimetype == "image/svg+xml":
                image = MIMEImage(content)
                image.add_header("Content-ID", f"<{filename}>")
                mail.attach(image)
            else:
                mail.attach(filename, content, mimetype)

    return mail


def _encode_attachments(
    attachments: typing.Sequence[typing.Tuple[str, bytes, str]] = None,
) -> list:
    if not attachments:
        return []
    return [
        {
            "filename": filename,
            "mimetype": mimetype,
            "content": base64.b64encode(content).decode("ascii"),
        }
        for filename, content, mimetype in attachments
    ]


def send_mail(
    *,
    title: str,
    recipient_list: typing.Sequence[str],
    template_name: str,
    template_variables: typing.Mapping,
    attachments: typing.Sequence[typing.Tuple[str, bytes, str]] = None,
    fail_without_raising: bool = False,
):
    text_message = render_to_string(f"{template_name}.txt", template_variables)
    html_message = mjml2html(
        render_to_string(f"{template_name}.mjml", template_variables)
    )

    mail = build_email(
        title=title,
        recipient_list=recipient_list,
        text_message=text_message,
        html_message=html_message,
        attachments=attachments,
    )

    try:
        return mail.send()
    except Exception as e:
        FailedEmail.objects.create(
            subject=title,
            recipients=list(recipient_list),
            text_body=text_message,
            html_body=html_message or "",
            attachments=_encode_attachments(attachments),
            error_message=str(e),
        )
        if not fail_without_raising:
            raise
        logger.exception("Failed to send mail '%s' to %s: %s", title, recipient_list, e)
        return 0


def resend_failed_email(failed_email: FailedEmail) -> int:
    """Rebuild and resend a previously failed email, deleting the record on success."""
    mail = build_email(
        title=failed_email.subject,
        recipient_list=failed_email.recipients,
        text_message=failed_email.text_body,
        html_message=failed_email.html_body,
        attachments=failed_email.decoded_attachments(),
    )
    sent = mail.send()
    failed_email.delete()
    return sent
