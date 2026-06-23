from unittest.mock import patch

from hexa.core.models import FailedEmail
from hexa.core.test import TestCase
from hexa.core.utils import resend_failed_email, send_mail


@patch("hexa.core.utils.mjml2html", return_value="<html></html>")
@patch("hexa.core.utils.render_to_string", return_value="body")
class SendMailTest(TestCase):
    def test_raises_by_default(self, _render, _mjml):
        with patch(
            "hexa.core.utils.EmailMultiAlternatives.send",
            side_effect=Exception("Authentication failed"),
        ):
            with self.assertRaises(Exception):
                send_mail(
                    title="Title",
                    recipient_list=["user@openhexa.org"],
                    template_name="some/template",
                    template_variables={},
                )
        self.assertEqual(FailedEmail.objects.count(), 1)

    def test_fail_without_raising_persists_and_returns_zero(self, _render, _mjml):
        with patch(
            "hexa.core.utils.EmailMultiAlternatives.send",
            side_effect=Exception("Authentication failed"),
        ):
            result = send_mail(
                title="Title",
                recipient_list=["user@openhexa.org"],
                template_name="some/template",
                template_variables={},
                attachments=[("logo.svg", b"<svg></svg>", "image/svg+xml")],
                fail_without_raising=True,
            )

        self.assertEqual(result, 0)
        failed = FailedEmail.objects.get()
        self.assertEqual(failed.subject, "Title")
        self.assertEqual(failed.recipients, ["user@openhexa.org"])
        self.assertEqual(failed.text_body, "body")
        self.assertIn("Authentication failed", failed.error_message)
        self.assertEqual(
            failed.decoded_attachments(),
            [("logo.svg", b"<svg></svg>", "image/svg+xml")],
        )

    def test_resend_failed_email_sends_and_deletes_record(self, _render, _mjml):
        failed = FailedEmail.objects.create(
            subject="Title",
            recipients=["user@openhexa.org"],
            text_body="body",
            html_body="<html></html>",
            error_message="Authentication failed",
        )

        with patch(
            "hexa.core.utils.EmailMultiAlternatives.send", return_value=1
        ) as mock_send:
            result = resend_failed_email(failed)

        mock_send.assert_called_once()
        self.assertEqual(result, 1)
        self.assertFalse(FailedEmail.objects.exists())

    def test_resend_failed_email_keeps_record_on_failure(self, _render, _mjml):
        failed = FailedEmail.objects.create(
            subject="Title",
            recipients=["user@openhexa.org"],
            text_body="body",
            html_body="<html></html>",
            error_message="Authentication failed",
        )

        with patch(
            "hexa.core.utils.EmailMultiAlternatives.send",
            side_effect=Exception("Connection refused"),
        ):
            with self.assertRaises(Exception):
                resend_failed_email(failed)

        self.assertTrue(FailedEmail.objects.filter(pk=failed.pk).exists())
