from django import test
from django.urls import reverse

from hexa.plugins.connector_s3.models import Credentials, Bucket, BucketPermission
from hexa.user_management.models import User, Team, Membership


class ConnectorS3Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim@bluesquarehub.com",
            "regular",
            is_superuser=True,
        )
        Membership.objects.create(team=cls.TEAM, user=cls.USER)
        cls.API_CREDENTIALS = Credentials.objects.create(
            username="app-iam-username",
            access_key_id="FOO",
            secret_access_key="BAR",
        )
        cls.BUCKET = Bucket.objects.create(
            s3_name="test-bucket", api_credentials=cls.API_CREDENTIALS
        )
        BucketPermission.objects.create(team=cls.TEAM, bucket=cls.BUCKET)

    def test_credentials_200(self):
        self.client.login(email="jim@bluesquarehub.com", password="regular")
        response = self.client.post(reverse("notebooks:credentials"))

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("username", response_data)
        self.assertEqual("jim@bluesquarehub.com", response_data["username"])
        self.assertIn("env", response_data)
        self.assertEqual(
            {
                "S3_TEST_BUCKET_BUCKET_NAME": "test-bucket",
                "S3_TEST_BUCKET_ACCESS_KEY_ID": "FOO",
                "S3_TEST_BUCKET_SECRET_ACCESS_KEY": "BAR",
            },
            response_data["env"],
        )
