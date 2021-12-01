import boto3
from django import test
from django.urls import reverse
from moto import mock_s3, mock_sts

from hexa.plugins.connector_s3.datacards import BucketCard, ObjectCard
from hexa.plugins.connector_s3.datagrids import ObjectGrid
from hexa.plugins.connector_s3.models import Bucket, Credentials, Object
from hexa.user_management.models import User


class ViewsTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.BUCKET = Bucket.objects.create(name="test-bucket")
        cls.OBJECT_FILE = Object.objects.create(
            bucket=cls.BUCKET, parent_key="/", key="test-object", size=200, type="file"
        )
        cls.OBJECT_DIRECTORY = Object.objects.create(
            bucket=cls.BUCKET,
            parent_key="/",
            key="test-directory",
            size=200,
            type="directory",
        )
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
            is_superuser=True,
            accepted_tos=True,
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
        self.assertIsInstance(response.context["object_grid"], ObjectGrid)

    def test_object_detail_200_file(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "connector_s3:object_detail",
                kwargs={"bucket_id": self.BUCKET.id, "path": self.OBJECT_FILE.key},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["datasource"], Bucket)
        self.assertIsInstance(response.context["object"], Object)
        self.assertIsInstance(response.context["object_card"], ObjectCard)
        self.assertIsNone(response.context["object_grid"])

    def test_object_detail_200_directory(self):
        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "connector_s3:object_detail",
                kwargs={"bucket_id": self.BUCKET.id, "path": self.OBJECT_DIRECTORY.key},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["object"], Object)
        self.assertIsInstance(response.context["object_card"], ObjectCard)
        self.assertIsInstance(response.context["object_grid"], ObjectGrid)

    @mock_s3
    @mock_sts
    def test_bucket_refresh(self):
        credentials = Credentials.objects.create(
            username="test-username",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="test-object", Body="XXX")
        s3_client.put_object(Bucket="test-bucket", Key="test-object-create", Body="YYY")

        self.client.force_login(self.USER_JANE)
        response = self.client.get(
            reverse(
                "connector_s3:object_refresh",
                kwargs={"bucket_id": self.BUCKET.id},
            )
            + "?object_key=test-object",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Object.objects.get(bucket__name="test-bucket", key="test-object").size, 3
        )

        response = self.client.get(
            reverse(
                "connector_s3:object_refresh",
                kwargs={"bucket_id": self.BUCKET.id},
            )
            + "?object_key=test-object-create",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Object.objects.get(
                bucket__name="test-bucket", key="test-object-create"
            ).size,
            3,
        )
