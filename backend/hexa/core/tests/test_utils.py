from unittest.mock import patch

from hexa.core.test import TestCase
from hexa.core.utils import send_mail


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

    def test_fail_without_raising_swallows_and_returns_zero(self, _render, _mjml):
        with patch(
            "hexa.core.utils.EmailMultiAlternatives.send",
            side_effect=Exception("Authentication failed"),
        ):
            result = send_mail(
                title="Title",
                recipient_list=["user@openhexa.org"],
                template_name="some/template",
                template_variables={},
                fail_without_raising=True,
            )
        self.assertEqual(result, 0)
