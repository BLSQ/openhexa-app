from django import test
from django.urls import reverse

from hexa.user_management.models import User


class NotebooksTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "john@bluesquarehub.com",
            "john@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )

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
        response_data = response.json()
        self.assertEqual(0, len(response_data))
