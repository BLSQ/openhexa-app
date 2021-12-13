from django import test
from django.urls import reverse

from hexa.core.datagrids import ActivityGrid
from hexa.user_management.models import User


class CoreTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "simi@bluesquarehub.com",
            "regular",
        )

    def test_index_200(self):
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)

    def test_dashboard_200(self):
        self.client.force_login(self.USER_REGULAR)
        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["last_activity_grid"], ActivityGrid)

    def test_ready_200(self):
        response = self.client.get(reverse("core:ready"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "ok")
