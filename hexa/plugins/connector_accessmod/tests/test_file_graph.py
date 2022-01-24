from django.conf import settings
from moto import mock_s3, mock_sts

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import FilesetFormat, FilesetRole, Project
from hexa.plugins.connector_s3.models import Bucket, Credentials
from hexa.user_management.models import User


class AccessmodFileGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks",
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            owner=cls.USER,
            spatial_resolution=100,
        )
        cls.ZONE_ROLE = FilesetRole.objects.create(
            name="Zone", format=FilesetFormat.RASTER
        )
        cls.CREDENTIALS = Credentials.objects.create(
            username="test-username",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        cls.BUCKET = Bucket.objects.create(name=settings.ACCESSMOD_S3_BUCKET_NAME)

    @mock_s3
    @mock_sts
    def test_full_upload_workflow(self):
        self.client.force_login(self.USER)

        # Step 1: create fileset
        r1 = self.run_query(
            """
                mutation createAccessmodFileset($input: CreateAccessmodFilesetInput) {
                  createAccessmodFileset(input: $input) {
                    success
                    fileset {
                        name
                        role {
                            id
                        }
                    }
                  }
                }
            """,
            {
                "input": {
                    "name": "A nice zone file",
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "roleId": str(self.ZONE_ROLE.id),
                }
            },
        )
        self.assertEqual(
            r1["data"]["createAccessmodFileset"],
            {
                "success": True,
                "fileset": {
                    "name": "A nice zone file",
                    "role": {"id": str(self.ZONE_ROLE.id)},
                },
            },
        )

        r2 = self.run_query(
            """
                mutation prepareAccessModFileUpload($input: PrepareAccessModFileUploadInput) {
                  prepareAccessModFileUpload(input: $input) {
                    success
                    uploadUrl
                    fileUri
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "mimeType": "text/csv",
                }
            },
        )

        self.assertEqual(
            r2["data"]["prepareAccessModFileUpload"]["success"],
            True,
        )
        self.assertTrue(
            r2["data"]["prepareAccessModFileUpload"]["uploadUrl"].startswith("https://")
        )
        self.assertIn(
            str(self.SAMPLE_PROJECT.id),
            r2["data"]["prepareAccessModFileUpload"]["uploadUrl"],
        )
        self.assertIn(
            "X-Amz-SignedHeaders", r2["data"]["prepareAccessModFileUpload"]["uploadUrl"]
        )
        self.assertTrue(
            r2["data"]["prepareAccessModFileUpload"]["fileUri"].startswith("s3://")
        )
        self.assertTrue(
            r2["data"]["prepareAccessModFileUpload"]["fileUri"].endswith(".csv")
        )
        self.assertIn(
            str(self.SAMPLE_PROJECT.id),
            r2["data"]["prepareAccessModFileUpload"]["fileUri"],
        )
