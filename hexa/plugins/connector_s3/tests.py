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
        cls.APP_CREDENTIALS = Credentials.objects.create(
            username="app-iam-username",
            access_key_id="FOO",
            secret_access_key="BAR",
        )
        cls.TEAM_CREDENTIALS = Credentials.objects.create(
            team=cls.TEAM,
            username="test-iam-username",
            access_key_id="FOO",
            secret_access_key="BAR",
        )
        cls.BUCKET = Bucket.objects.create(
            name="test-bucket", sync_credentials=cls.APP_CREDENTIALS
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
            response_data["env"],
            {
                "AWS_ACCESS_KEY_ID": "FOO",
                "AWS_SECRET_ACCESS_KEY": "BAR",
                "S3_BUCKET_NAMES": "test-bucket",
            },
        )
