from django import test
from django.urls import reverse

from hexa.user_management.models import User


class AuthTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "john@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )

    def test_any_page_anonymous_302(self):
        response = self.client.get(reverse("core:dashboard"))

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/?next=/dashboard")

    def test_any_page_anonymous_200(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_logout_302(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("logout"))

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_account_200(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("user:account"))

        self.assertEqual(response.status_code, 200)

    def test_credentials_200(self):
        self.client.login(email="john@bluesquarehub.com", password="regular")
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("username", response_data)
        self.assertEqual("john@bluesquarehub.com", response_data["username"])

    def test_credentials_401(self):
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 401)
