from django import test
from django.urls import reverse

from hexa.plugins.connector_s3.models import S3Credentials
from hexa.user_management.models import User


class ConnectorS3Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_REGULAR = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )
        S3Credentials.objects.create(
            user=cls.USER_REGULAR,
            username="test-iam-username",
            access_key_id="FOO",
            secret_access_key="BAR",
        )

    def test_credentials_200(self):
        self.client.login(email="jim@bluesquarehub.com", password="regular")
        response = self.client.get(reverse("user:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("username", response_data)
        self.assertEqual("jim@bluesquarehub.com", response_data["username"])
        self.assertIn("env", response_data)
        self.assertEqual(
            response_data["env"],
            {
                "AWS_ACCESS_KEY_ID": "FOO",
                "AWS_SECRET_ACCESS_KEY": "BAR",
            },
        )
