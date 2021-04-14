from django import test
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from hexa.user_management.models import User, Team
from hexa.catalog.models import Datasource, CatalogIndexQuerySet
from ..models import Instance, DataElement, Indicator, InstancePermission


class ConnectorDhis2Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_BJORN = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjorn@bluesquarehub.com",
            "bjornbjorn",
        )
        cls.USER_KRISTEN = User.objects.create_user(
            "kristen@bluesquarehub.com",
            "kristen@bluesquarehub.com",
            "kristen2000",
            is_superuser=True,
        )
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            hexa_name="DHIS2 Play",
            hexa_short_name="Play",
            hexa_description="The DHIS2 official demo instance with realistic sample medical data",
            api_url="https://play.dhis2.org/demo",
            api_username="admin",
            api_password="district",
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

    def test_catalog_index_empty_200(self):
        """Bjorn is not a superuser, he can see the catalog but it will be empty."""
        self.client.force_login(self.USER_BJORN)

        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, response.context["datasource_indexes"].count())

    def test_catalog_index_200(self):
        """As a superuser, Kristen can list datasources."""

        self.client.force_login(self.USER_KRISTEN)

        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, response.context["datasource_indexes"].count())

    def test_catalog_search_empty_200(self):
        """Bjorn is not a superuser, he can see the catalog but it will be empty."""

        self.client.force_login(self.USER_BJORN)

        response = self.client.post(reverse("catalog:search"), data={"query": "anc"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], CatalogIndexQuerySet)
        self.assertEqual(0, response.context["results"].count())

    def test_catalog_search_200(self):
        """As a superuser, Kristen can search for content."""

        self.client.force_login(self.USER_KRISTEN)

        response = self.client.post(reverse("catalog:search"), data={"query": "anc"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], CatalogIndexQuerySet)
        self.assertEqual(3, response.context["results"].count())

    def test_catalog_search_datasource_200(self):
        self.client.force_login(self.USER_KRISTEN)

        response = self.client.post(
            reverse("catalog:search"), data={"query": "play type:dhis2_instance"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], CatalogIndexQuerySet)
        self.assertEqual(1, len(response.context["results"]))

    def test_catalog_search_data_element_200(self):
        self.client.force_login(self.USER_KRISTEN)

        response = self.client.post(
            reverse("catalog:search"), data={"query": "anc type:dhis2_dataelement"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], CatalogIndexQuerySet)
        self.assertEqual(2, response.context["results"].count())

    def test_catalog_search_indicator_200(self):
        self.client.force_login(self.USER_KRISTEN)

        response = self.client.post(
            reverse("catalog:search"), data={"query": "anc type:dhis2_indicator"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["results"], CatalogIndexQuerySet)
        self.assertEqual(1, response.context["results"].count())

    def test_catalog_quick_search_empty_200(self):
        """Bjorn is not a superuser, he can try to search for content but there will be no results"""

        self.client.force_login(self.USER_BJORN)

        response = self.client.get(f"{reverse('catalog:quick_search')}?query=anc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.json()["results"]))

    def test_catalog_quick_search_200(self):
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
                and r["name"] == "ANC First visit"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Data Element"
                and r["name"] == "ANC Second visit"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Indicator"
                and r["name"] == "Ante-Natal Care visits"
            )
        )

        # "display" should match 1 data source and 1 indicator
        response = self.client.get(f"{reverse('catalog:quick_search')}?query=medical")
        results = response.json()["results"]
        self.assertEqual(2, len(results))
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Instance"
                and r["name"] == "DHIS2 Play"
            )
        )
        self.assertTrue(
            any(
                r
                for r in results
                if r["app_label"] == "connector_dhis2"
                and r["content_type_name"] == "DHIS2 Indicator"
                and r["name"] == "Medical displays"
            )
        )

    def test_datasource_detail_404(self):
        """Bjorn is not a superuser, he can't access the datasource detail page."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:datasource_detail",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_datasource_detail_200(self):
        """As a superuser, Kristen can access any datasource detail screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:datasource_detail",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Datasource)
        self.assertIsInstance(response.context["data_elements_list_params"], dict)
        self.assertIsInstance(response.context["indicators_list_params"], dict)

    @test.tag("external")
    def test_datasource_sync_404(self):
        """Bjorn is not a superuser, he can't sync datasources."""

        self.client.force_login(self.USER_BJORN)
        http_referer = (
            f"https://localhost/catalog/datasource/{self.DHIS2_INSTANCE_PLAY.pk}"
        )
        response = self.client.get(
            reverse(
                "connector_dhis2:datasource_sync",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
            HTTP_REFERER=http_referer,
        )

        self.assertEqual(response.status_code, 404)

    @test.tag("external")
    def test_datasource_sync_302(self):
        """As a superuser, Kristen can sync every datasource."""

        self.client.force_login(self.USER_KRISTEN)
        http_referer = (
            f"https://localhost/catalog/datasource/{self.DHIS2_INSTANCE_PLAY.pk}"
        )
        response = self.client.get(
            reverse(
                "connector_dhis2:datasource_sync",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
            HTTP_REFERER=http_referer,
        )

        # Check that the response is temporary redirection to referer
        self.assertEqual(response.status_code, 302)
        self.assertEqual(http_referer, response.url)

        # Test that all data elements have a value type and an aggregation type
        self.assertEqual(0, len(DataElement.objects.filter(value_type=None)))
        self.assertEqual(0, len(DataElement.objects.filter(aggregation_type=None)))

    def test_data_elements_404(self):
        """Bjorn is not a superuser, he can't access the data elements page."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_list",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_data_elements_200(self):
        """As a superuser, Kristen can see the data elements screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_list",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Datasource)
        self.assertIsInstance(response.context["data_elements_list_params"], dict)

    def test_indicators_404(self):
        """As Bjorn is not a superuser, he can't access the indicators screen."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_list",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_indicators_200(self):
        """As a superuser, Kristen can see the data elements screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_list",
                kwargs={"datasource_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Datasource)
        self.assertIsInstance(response.context["indicators_list_params"], dict)
