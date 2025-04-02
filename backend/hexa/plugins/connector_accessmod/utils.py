import typing

from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string

from hexa.plugins.connector_accessmod.models import AccessmodProfile


def send_mail_to_accessmod_superusers(
    *, title: str, template_name: str, template_variables: typing.Mapping
):
    html_message = render_to_string(
        f"{template_name}.html",
        template_variables,
    )
    text_message = render_to_string(
        f"{template_name}.txt",
        template_variables,
    )

    accessmod_admin_emails = [
        p.user.email
        for p in AccessmodProfile.objects.filter(is_accessmod_superuser=True)
    ]

    django_send_mail(
        title,
        message=text_message,
        html_message=html_message,
        recipient_list=accessmod_admin_emails,
        from_email=None,  # TODO: check
    )


def send_mail(
    *,
    title: str,
    recipient_list: typing.Sequence[str],
    template_name: str,
    template_variables: typing.Mapping,
):
    html_message = render_to_string(
        f"{template_name}.html",
        template_variables,
    )
    text_message = render_to_string(
        f"{template_name}.txt",
        template_variables,
    )

    django_send_mail(
        title,
        message=text_message,
        html_message=html_message,
        recipient_list=recipient_list,
        from_email=None,  # TODO: check
    )
