from unittest import skip

from django import test
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from hexa.user_management.models import Team, User

from ..models import DataElement, Indicator, Instance, InstancePermission


class ConnectorDhis2Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
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
            url="https://play.dhis2.org",
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

    def test_instance_detail_404(self):
        """Bjorn is not a superuser, he can't access the datasource detail page."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:instance_detail",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_instance_detail_200(self):
        """As a superuser, Kristen can access any datasource detail screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:instance_detail",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["instance"], Instance)

    @test.tag("external")
    @skip("Deactivated for now - mocks needed")
    def test_instance_sync_404(self):
        """Bjorn is not a superuser, he can't sync datasources."""

        self.client.force_login(self.USER_BJORN)
        http_referer = (
            f"https://localhost/catalog/datasource/{self.DHIS2_INSTANCE_PLAY.pk}"
        )
        response = self.client.get(
            reverse(
                "connector_dhis2:instance_sync",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
            HTTP_REFERER=http_referer,
        )

        self.assertEqual(response.status_code, 404)

    @test.tag("external")
    @skip("Deactivated for now - mocks needed")
    def test_instance_sync_302(self):
        """As a superuser, Kristen can sync every datasource."""

        self.client.force_login(self.USER_KRISTEN)
        http_referer = (
            f"https://localhost/catalog/datasource/{self.DHIS2_INSTANCE_PLAY.pk}"
        )
        response = self.client.get(
            reverse(
                "connector_dhis2:instance_sync",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
            HTTP_REFERER=http_referer,
        )

        # Check that the response is temporary redirection to referer
        self.assertEqual(response.status_code, 302)
        self.assertEqual(http_referer, response.url)

        # Test that all data elements have a value type and an aggregation type
        self.assertEqual(0, len(DataElement.objects.filter(dhis2_value_type=None)))
        self.assertEqual(
            0, len(DataElement.objects.filter(dhis2_aggregation_type=None))
        )

    def test_data_elements_404(self):
        """Bjorn is not a superuser, he can't access the data elements page."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_data_elements_200(self):
        """As a superuser, Kristen can see the data elements screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["instance"], Instance)

    def test_indicators_404(self):
        """As Bjorn is not a superuser, he can't access the indicators screen."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_indicators_200(self):
        """As a superuser, Kristen can see the data elements screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["instance"], Instance)
