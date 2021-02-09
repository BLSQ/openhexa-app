from django import test
from django.conf import settings
from django.urls import reverse
import uuid

from habari.auth.models import User


class CatalogTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "regular@bluesquarehub.com",
            "regular@bluesquarehub.com",
            "regular",
        )

    def test_datasource_sync_login_302(self):
        response = self.client.get(
            reverse(
                "catalog:datasource_sync",
                kwargs={"datasource_id": uuid.uuid4()},
            ),
        )

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response.url)

    def test_datasource_sync_404(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get(
            reverse("catalog:datasource_sync", kwargs={"datasource_id": uuid.uuid4()})
        )

        # Check that the response is temporary redirection to /login.
        self.assertEqual(response.status_code, 404)
