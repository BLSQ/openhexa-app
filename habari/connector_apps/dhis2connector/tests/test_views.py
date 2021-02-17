from django import test
from django.urls import reverse

from habari.auth.models import User
from habari.catalog.models import Datasource
from ..models import Dhis2Connector


class CatalogTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "regular@bluesquarehub.com",
            "regular@bluesquarehub.com",
            "regular",
        )

        cls.DATASOURCE_DHIS2_PLAY = Datasource.objects.create(
            name="DHIS2 Play", datasource_type="DHIS2"
        )
        cls.DATASOURCE_CONNECTION_DHIS2_PLAY = Dhis2Connector.objects.create(
            datasource=cls.DATASOURCE_DHIS2_PLAY,
            api_url="https://play.dhis2.org/demo",
            api_username="admin",
            api_password="district",
        )

    @test.tag("external")
    def test_datasource_sync_success_302(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        http_referer = (
            f"https://localhost/catalog/datasource/{self.DATASOURCE_DHIS2_PLAY.id}"
        )
        response = self.client.get(
            reverse(
                "catalog:datasource_sync",
                kwargs={"datasource_id": self.DATASOURCE_DHIS2_PLAY.id},
            ),
            HTTP_REFERER=http_referer,
        )

        # Check that the response is temporary redirection to .
        self.assertEqual(response.status_code, 302)
        self.assertEqual(http_referer, response.url)

    def test_data_elements_200(self):
        self.client.login(email="regular@bluesquarehub.com", password="regular")
        response = self.client.get(
            reverse(
                "dhis2connector:data_element_list",
                kwargs={"datasource_id": self.DATASOURCE_DHIS2_PLAY.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
