import os
import typing
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from mjml import mjml2html


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


def send_mail(
    *,
    title: str,
    recipient_list: typing.Sequence[str],
    template_name: str,
    template_variables: typing.Mapping,
    attachments: typing.Sequence[typing.Tuple[str, bytes, str]] = None,
):
    text_message = render_to_string(f"{template_name}.txt", template_variables)
    html_message = mjml2html(
        render_to_string(f"{template_name}.mjml", template_variables)
    )

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
            if mimetype.startswith("image/"):
                image = MIMEImage(content)
                image.add_header("Content-ID", f"<{filename}>")
                mail.attach(image)
            else:
                mail.attach(filename, content, mimetype)

    return mail.send()
