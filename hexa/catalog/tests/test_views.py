from django import test
from django.db.models import QuerySet
from django.http import JsonResponse
from django.urls import reverse

from hexa.user_management.models import User


class CatalogTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

    def test_catalog_index_200(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "catalog:index",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource_indexes"], QuerySet)

    def test_catalog_quick_search_200(self):
        self.client.force_login(self.USER_JANE)

        response = self.client.get(f"{reverse('catalog:quick_search')}?query=test")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        response_data = response.json()
        self.assertIn("results", response_data)
        self.assertEqual(0, len(response_data["results"]))
