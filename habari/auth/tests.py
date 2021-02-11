from django import test
from django.conf import settings
from django.urls import reverse

from habari.auth.models import User


class AuthTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "regular@bluesquarehub.com",
            "regular@bluesquarehub.com",
            "regular",
        )

    def test_any_page_anonymous_302(self):
        response = self.client.get(reverse("dashboard:index"))

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response.url)

    def test_any_page_anonymous_200(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("dashboard:index"))

        self.assertEqual(response.status_code, 200)

    def test_logout_302(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("auth:logout"))

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response.url)

    def test_login_200(self):
        response = self.client.get(reverse("auth:login"))

        self.assertEqual(response.status_code, 200)

    def test_account_200(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("auth:account"))

        self.assertEqual(response.status_code, 200)
