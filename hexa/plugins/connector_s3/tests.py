from django import test
from django.urls import reverse

from hexa.plugins.connector_s3.models import Credentials, Bucket
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
        cls.USER_CREDENTIALS = Credentials.objects.create(
            user=cls.USER_REGULAR,
            username="test-iam-username",
            access_key_id="FOO",
            secret_access_key="BAR",
        )
        Bucket.objects.create(name="test-bucket", sync_credentials=cls.USER_CREDENTIALS)

    def test_credentials_200(self):
        self.client.login(email="jim@bluesquarehub.com", password="regular")
        response = self.client.post(reverse("notebooks:credentials"))

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
                "S3_BUCKET_NAMES": "test-bucket",
            },
        )
