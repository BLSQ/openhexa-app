from django import test
from django.urls import reverse

from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bucket = Bucket.objects.create(name="test-bucket")
        cls.user_jane = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )

    def test_detail_200(self):
        self.client.force_login(self.user_jane)
        response = self.client.get(
            reverse(
                "connector_s3:datasource_detail",
                kwargs={"datasource_id": self.bucket.id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Bucket)
