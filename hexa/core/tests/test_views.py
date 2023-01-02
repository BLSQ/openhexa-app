from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import User


class CoreTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "simi@bluesquarehub.com",
            "regular_password",
        )

    def test_ready_200(self):
        response = self.client.get(reverse("core:ready"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "ok")

    def test_redirection_success(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 302)
