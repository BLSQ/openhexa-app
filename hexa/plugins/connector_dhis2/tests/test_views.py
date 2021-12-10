from django import test
from django.urls import reverse
from django.utils import timezone

from hexa.user_management.models import Team, User

from ..datacards import (
    DataElementCard,
    DatasetCard,
    IndicatorCard,
    OrganisationUnitCard,
)
from ..datagrids import (
    DataElementGrid,
    DatasetGrid,
    IndicatorGrid,
    OrganisationUnitGrid,
)
from ..models import (
    DataElement,
    DataSet,
    Indicator,
    Instance,
    InstancePermission,
    OrganisationUnit,
)


class ConnectorDhis2Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_BJORN = User.objects.create_user(
            "bjorn@bluesquarehub.com",
            "bjornbjorn",
            accepted_tos=True,
        )
        cls.USER_KRISTEN = User.objects.create_user(
            "kristen@bluesquarehub.com",
            "kristen2000",
            is_superuser=True,
            accepted_tos=True,
        )
        cls.DHIS2_INSTANCE_PLAY = Instance.objects.create(
            url="https://play.dhis2.org.invalid",
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
        cls.ORG_UNIT_1 = OrganisationUnit.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="kamalOUYDD1",
            name="Region1",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            leaf=False,
            code="OU_1",
            path="kamalOUYDD1",
        )
        cls.ORG_UNIT_2 = OrganisationUnit.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="kamalOUYDD2",
            name="SubRegion",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            leaf=False,
            code="OU_2",
            path="kamalOUYDD1.kamalOUYDD2",
        )
        cls.ORG_UNIT_3 = OrganisationUnit.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="kamalOUYDD3",
            name="SubRegionChieftain",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
            leaf=True,
            code="OU_3",
            path="kamalOUYDD1.kamalOUYDD02.kamalOUYDD3",
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
        cls.DATASET_1 = DataSet.objects.create(
            instance=cls.DHIS2_INSTANCE_PLAY,
            dhis2_id="oNzq8duNBx7",
            name="Malaria",
            code="malaria",
            created=timezone.now(),
            last_updated=timezone.now(),
            external_access=False,
            favorite=False,
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

    def test_data_element_list_404(self):
        """Bjorn is not a superuser, he can't access the data elements page."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_data_element_list_200(self):
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
        self.assertIsInstance(response.context["data_element_grid"], DataElementGrid)
        self.assertEqual(3, len(response.context["data_element_grid"]))

    def test_data_element_download_400(self):
        """No filename, no download."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_download",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_data_element_download_200(self):
        """Valid download request."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_download",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            )
            + "?filename=test.csv",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("text/csv", response.headers["Content-Type"])
        self.assertEqual(
            "attachment;filename=test.csv", response.headers["Content-Disposition"]
        )

    def test_data_element_detail_200(self):
        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:data_element_detail",
                kwargs={
                    "instance_id": self.DHIS2_INSTANCE_PLAY.id,
                    "data_element_id": self.DATA_ELEMENT_1.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["data_element"], DataElement)
        self.assertIsInstance(response.context["data_element_card"], DataElementCard)

    def test_organisation_list_200(self):
        """As a superuser, Kristen can see the organisation unit screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:organisation_unit_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["instance"], Instance)
        self.assertIsInstance(
            response.context["organisation_unit_grid"], OrganisationUnitGrid
        )
        self.assertEqual(3, len(response.context["organisation_unit_grid"]))

    def test_organisation_detail_200(self):
        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:organisation_unit_detail",
                kwargs={
                    "instance_id": self.DHIS2_INSTANCE_PLAY.id,
                    "organisation_unit_id": self.ORG_UNIT_1.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["organisation_unit"], OrganisationUnit)
        self.assertIsInstance(
            response.context["organisation_unit_card"], OrganisationUnitCard
        )
        self.assertEqual(1, len(response.context["sub_organisation_unit_grid"]))

    def test_indicator_list_404(self):
        """As Bjorn is not a superuser, he can't access the indicators screen."""

        self.client.force_login(self.USER_BJORN)
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_indicator_list_200(self):
        """As a superuser, Kristen can see the indicators screen."""

        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["instance"], Instance)
        self.assertIsInstance(response.context["indicator_grid"], IndicatorGrid)
        self.assertEqual(2, len(response.context["indicator_grid"]))

    def test_indicator_detail_200(self):
        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:indicator_detail",
                kwargs={
                    "instance_id": self.DHIS2_INSTANCE_PLAY.id,
                    "indicator_id": self.DATA_INDICATOR_1.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["indicator"], Indicator)
        self.assertIsInstance(response.context["indicator_card"], IndicatorCard)

    def test_dataset_list_200(self):
        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:dataset_list",
                kwargs={"instance_id": self.DHIS2_INSTANCE_PLAY.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["instance"], Instance)
        self.assertIsInstance(response.context["dataset_grid"], DatasetGrid)
        self.assertEqual(1, len(response.context["dataset_grid"]))

    def test_dataset_detail_200(self):
        self.client.force_login(self.USER_KRISTEN)
        response = self.client.get(
            reverse(
                "connector_dhis2:dataset_detail",
                kwargs={
                    "instance_id": self.DHIS2_INSTANCE_PLAY.id,
                    "dataset_id": self.DATASET_1.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["dataset"], DataSet)
        self.assertIsInstance(response.context["dataset_card"], DatasetCard)
