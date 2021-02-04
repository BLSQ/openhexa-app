from django.conf import settings
from django import test

from habari.auth.models import User


class SimpleTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.REGULAR_USER = User.objects.create_user(
            "regular@bluesquarehub.com", "regular@bluesquarehub.com", "regular",
        )

    def test_index_redirects_to_login(self):
        response = self.client.get("/")

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login", response.url)

    def test_login_200(self):
        response = self.client.get(settings.LOGIN_URL)

        self.assertEqual(response.status_code, 200)

    def test_account_302(self):
        response = self.client.get("/auth/account/")

        self.assertEqual(response.status_code, 302)

    def test_account_200(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get("/auth/account/")

        self.assertEqual(response.status_code, 200)
