from django import test
from moto import mock_iam, mock_sts

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_s3.credentials import notebooks_credentials
from hexa.plugins.connector_s3.models import Bucket, BucketPermission, Credentials
from hexa.user_management.models import Team, User


class CredentialsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
        )
        cls.TEAM_HEXA = Team.objects.create(name="Hexa Team!")
        cls.USER_JANE.team_set.add(cls.TEAM_HEXA)
        cls.CREDENTIALS = Credentials.objects.create(
            username="hexa-app-test",
            access_key_id="foo",
            secret_access_key="bar",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )

    @mock_iam
    @mock_sts
    def test_credentials(self):
        credentials = NotebooksCredentials(self.USER_JANE)
        buckets = [
            Bucket.objects.create(name="hexa-test-bucket-1"),
            Bucket.objects.create(name="hexa-test-bucket-2"),
        ]
        for bucket in buckets:
            BucketPermission.objects.create(team=self.TEAM_HEXA, bucket=bucket)

        notebooks_credentials(credentials)
        self.assertEqual("false", credentials.env["HEXA_FEATURE_FLAG_S3FS"])
        self.assertEqual(
            "hexa-test-bucket-1,hexa-test-bucket-2",
            credentials.env["AWS_S3_BUCKET_NAMES"],
        )
        for key in [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "AWS_DEFAULT_REGION",
        ]:
            self.assertIsInstance(credentials.env[key], str)
            self.assertGreater(len(credentials.env[key]), 0)
