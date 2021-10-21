from django import test
from django.urls import reverse

from hexa.plugins.connector_s3.datacards import BucketCard
from hexa.plugins.connector_s3.datagrids import ObjectGrid
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.BUCKET = Bucket.objects.create(name="test-bucket")
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

    def test_datasource_detail_200(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "connector_s3:datasource_detail",
                kwargs={"datasource_id": self.BUCKET.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Bucket)
        self.assertIsInstance(response.context["bucket_card"], BucketCard)
        self.assertIsInstance(response.context["datagrid"], ObjectGrid)
