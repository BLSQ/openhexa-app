from django import test
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from hexa.core.models import BaseIndexQuerySet
from hexa.plugins.connector_dhis2.models import (
    DataElement,
    Indicator,
    Instance,
    InstancePermission,
)
from hexa.user_management.models import Team, User


class SearchTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_BJORN = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjornbjorn",
        )
        cls.USER_KRISTEN = User.objects.create_user(
            "kristen@bluesquarehub.com",
            "kristen2000",
            is_superuser=True,
        )
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org", name="DHIS2 Play"
        )
        InstancePermission.objects.create(
            team=cls.TEAM, instance=cls.DHIS2_INSTANCE_PLAY
        )
        cls.DATA_ELEMENT_1 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="O1BccPF5yci",
            name="ANC First visit",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
        )
        cls.DATA_ELEMENT_2 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="eLW6jbvVcPZ",
            name="ANC Second visit",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
        )
        cls.DATA_ELEMENT_3 = DataElement.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="kmaHyZXMHCz",
            name="C-sections",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
        )
        cls.DATA_INDICATOR_1 = Indicator.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="xaG3AfYG2Ts",
            name="Ante-Natal Care visits",
            description="Uses different ANC data indicators",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            annualized=False,
        )
        cls.DATA_INDICATOR_2 = Indicator.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="oNzq8duNBx6",
            name="Medical displays",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            annualized=False,
        )

    def test_catalog_quick_search_200(self):
        self.client.force_login(self.USER_JANE)

        response = self.client.get(f"{reverse('catalog:quick_search')}?query=test")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        response_data = response.json()
        self.assertIn("results", response_data)
        self.assertEqual(0, len(response_data["results"]))

    def test_catalog_search_empty_200(self):
        """Bjorn is not a superuser, he can see the catalog but it will be empty."""

        self.client.force_login(self.USER_BJORN)

        response = self.client.get(reverse("catalog:search"), data={"query": "anc"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], BaseIndexQuerySet)
        self.assertEqual(0, response.context["results"].count())

    def test_catalog_search_200(self):
        """As a superuser, Kristen can search for content."""

        self.client.force_login(self.USER_KRISTEN)

        response = self.client.get(reverse("catalog:search"), data={"query": "anc"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], BaseIndexQuerySet)
        self.assertEqual(3, response.context["results"].count())

    def test_catalog_search_datasource_200(self):
        self.client.force_login(self.USER_KRISTEN)

        response = self.client.get(
            reverse("catalog:search"), data={"query": "play type:dhis2_instance"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], BaseIndexQuerySet)
        self.assertEqual(1, len(response.context["results"]))

    def test_catalog_search_data_element_200(self):
        self.client.force_login(self.USER_KRISTEN)

        response = self.client.get(
            reverse("catalog:search"), data={"query": "anc type:dhis2_dataelement"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], BaseIndexQuerySet)
        self.assertEqual(2, response.context["results"].count())

    def test_catalog_search_indicator_200(self):
        self.client.force_login(self.USER_KRISTEN)

        response = self.client.get(
            reverse("catalog:search"), data={"query": "anc type:dhis2_indicator"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], BaseIndexQuerySet)
        self.assertEqual(1, response.context["results"].count())

    def test_catalog_quick_search_empty_200(self):
        """Bjorn is not a superuser, he can try to search for content but there will be no results"""

        self.client.force_login(self.USER_BJORN)

        response = self.client.get(f"{reverse('catalog:quick_search')}?query=anc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.json()["results"]))

    def test_catalog_quick_search_200_kristen(self):
        """As a superuser, Kristen can search for content."""

        self.client.force_login(self.USER_KRISTEN)

        # "foo" should have zero matches
        response = self.client.get(f"{reverse('catalog:quick_search')}?query=foo")
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()["results"]))

        # "anc" should match 2 data elements and 1 indicator
        response = self.client.get(f"{reverse('catalog:quick_search')}?query=anc")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        results = response.json()["results"]
        self.assertEqual(3, len(results))
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Data Element"
                and r["external_name"] == "ANC First visit"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Data Element"
                and r["external_name"] == "ANC Second visit"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Indicator"
                and r["external_name"] == "Ante-Natal Care visits"
            )
        )

        # "display" should match 1 data source and 1 indicator
        response = self.client.get(f"{reverse('catalog:quick_search')}?query=display")
        results = response.json()["results"]
        self.assertEqual(2, len(results))
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Instance"
                and r["external_name"] == "DHIS2 Play"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Indicator"
                and r["external_name"] == "Medical displays"
            )
        )
