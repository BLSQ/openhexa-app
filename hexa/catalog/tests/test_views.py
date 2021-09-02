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
