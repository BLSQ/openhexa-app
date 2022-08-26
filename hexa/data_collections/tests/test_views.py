from django.http import JsonResponse
from django.urls import reverse

from hexa.core.test import TestCase
from hexa.data_collections.models import Collection
from hexa.user_management.models import Feature, FeatureFlag, User


class CollectionViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

        cls.USER_BJORN = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjornbjorn",
        )
        cls.USER_KRISTEN = User.objects.create_user(
            "kristen@bluesquarehub.com",
            "kristen2000",
            is_superuser=True,
        )
        cls.COLLECTION_1 = Collection.objects.create(name="Malaria Collection")
        cls.COLLECTION_2 = Collection.objects.create(
            name="RDC: Ministry of health documents"
        )

    def test_quick_search_no_feature_flag(self):
        self.client.force_login(self.USER_JANE)

        response = self.client.get(f"{reverse('catalog:quick_search')}?query=malaria")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        response_data = response.json()
        self.assertIn("results", response_data)
        self.assertEqual(0, len(response_data["results"]))

    def test_quick_search_results(self):
        feature = Feature.objects.create(code="collections")
        FeatureFlag.objects.create(feature=feature, user=self.USER_JANE)
        self.client.force_login(self.USER_JANE)

        response = self.client.get(f"{reverse('catalog:quick_search')}?query=malaria")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        response_data = response.json()
        self.assertIn("results", response_data)
        self.assertEqual(1, len(response_data["results"]))
