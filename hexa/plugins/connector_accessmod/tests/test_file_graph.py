from django.conf import settings
from moto import mock_s3, mock_sts

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    File,
    Fileset,
    FilesetFormat,
    FilesetRole,
    Project,
)
from hexa.plugins.connector_s3.models import Bucket, Credentials
from hexa.user_management.models import User


class AccessmodFileGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimrocks",
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janesthebest",
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            owner=cls.USER_1,
            spatial_resolution=100,
        )
        cls.ZONE_ROLE = FilesetRole.objects.create(
            name="Zone", format=FilesetFormat.RASTER
        )
        cls.SAMPLE_FILESET = Fileset.objects.create(
            name="A cool fileset",
            role=cls.ZONE_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.SAMPLE_FILE_1 = File.objects.create(
            fileset=cls.SAMPLE_FILESET, uri="afile.csv", mime_type="text/csv"
        )
        cls.SAMPLE_FILE_2 = File.objects.create(
            fileset=cls.SAMPLE_FILESET, uri="anotherfile.csv", mime_type="text/csv"
        )
        cls.CREDENTIALS = Credentials.objects.create(
            username="test-username",
            default_region="eu-central-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        cls.BUCKET = Bucket.objects.create(name=settings.ACCESSMOD_S3_BUCKET_NAME)

    def test_accessmod_fileset_owner(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFileset($id: String!) {
                  accessmodFileset(id: $id) {
                    id
                    name
                    role {
                        id
                    }
                    owner {
                        id
                    }
                    files {
                        id
                        mimeType
                        uri
                    }
                  }
                }
            """,
            {"id": str(self.SAMPLE_FILESET.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFileset"],
            {
                "id": str(self.SAMPLE_FILESET.id),
                "name": self.SAMPLE_FILESET.name,
                "role": {"id": str(self.SAMPLE_FILESET.role_id)},
                "owner": {"id": str(self.SAMPLE_FILESET.owner_id)},
                "files": [
                    {"id": str(f.id), "mimeType": f.mime_type, "uri": f.uri}
                    for f in self.SAMPLE_FILESET.file_set.all()
                ],
            },
        )

    def test_accessmod_fileset_not_owner(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodFileset($id: String!) {
                  accessmodFileset(id: $id) {
                    id
                  }
                }
            """,
            {"id": str(self.SAMPLE_FILESET.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFileset"],
            None,
        )

    def test_accessmod_filesets(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFilesets {
                  accessmodFilesets {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {"id": str(self.SAMPLE_FILESET.id)},
                ],
            },
        )

    def test_accessmod_filesets_empty(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodFilesets {
                  accessmodFilesets {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 0,
                "items": [],
            },
        )

    @mock_s3
    @mock_sts
    def test_full_accessmod_upload_workflow(self):
        self.client.force_login(self.USER_1)

        # Step 1: create fileset
        r1 = self.run_query(
            """
                mutation createAccessmodFileset($input: CreateAccessmodFilesetInput) {
                  createAccessmodFileset(input: $input) {
                    success
                    fileset {
                        id
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
        self.assertEqual(True, r1["data"]["createAccessmodFileset"]["success"])
        self.assertEqual(
            "A nice zone file", r1["data"]["createAccessmodFileset"]["fileset"]["name"]
        )
        self.assertEqual(
            {"id": str(self.ZONE_ROLE.id)},
            r1["data"]["createAccessmodFileset"]["fileset"]["role"],
        )
        fileset_id = r1["data"]["createAccessmodFileset"]["fileset"]["id"]

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
        file_uri = r2["data"]["prepareAccessModFileUpload"]["fileUri"]

        r3 = self.run_query(
            """
                mutation createAccessModFile($input: CreateAccessModFileInput) {
                    createAccessModFile(input: $input) {
                        success
                        file {
                            id
                            uri
                            mimeType
                            fileset {
                                id
                            }
                        }
                    }
                }
            """,
            {
                "input": {
                    "filesetId": fileset_id,
                    "uri": file_uri,
                    "mimeType": "text/csv",
                }
            },
        )
        self.assertEqual(True, r3["data"]["createAccessModFile"]["success"])
        self.assertEqual(file_uri, r3["data"]["createAccessModFile"]["file"]["uri"])
        self.assertEqual(
            "text/csv", r3["data"]["createAccessModFile"]["file"]["mimeType"]
        )
        self.assertEqual(
            fileset_id, r3["data"]["createAccessModFile"]["file"]["fileset"]["id"]
        )
        file_id = r3["data"]["createAccessModFile"]["file"]["id"]

        # The fileset updated_at value should be equal to the created_at of the most recent file
        fileset = Fileset.objects.get(id=fileset_id)
        file = File.objects.get(id=file_id)
        self.assertGreater(fileset.updated_at, file.created_at)

    def test_delete_fileset(self):
        self.client.force_login(self.USER_1)
        fileset = Fileset.objects.create(
            name="About to be deleted",
            role=self.ZONE_ROLE,
            project=self.SAMPLE_PROJECT,
            owner=self.USER_1,
        )

        r = self.run_query(
            """
                mutation deleteAccessmodFileset($input: DeleteAccessmodFilesetInput) {
                  deleteAccessmodFileset(input: $input) {
                    success
                  }
                }
            """,
            {"input": {"id": str(fileset.id)}},
        )
        self.assertEqual(True, r["data"]["deleteAccessmodFileset"]["success"])
        self.assertEqual(False, Fileset.objects.filter(id=fileset.id).exists())

    def test_delete_file(self):
        self.client.force_login(self.USER_1)
        fileset = Fileset.objects.create(
            name="About to be deleted",
            role=self.ZONE_ROLE,
            project=self.SAMPLE_PROJECT,
            owner=self.USER_1,
        )
        original_fileset_updated_at = fileset.updated_at
        file = File.objects.create(
            fileset=fileset, uri="notreallyanuri.csv", mime_type="text_csv"
        )

        r = self.run_query(
            """
                mutation deleteAccessmodFile($input: DeleteAccessmodFileInput) {
                  deleteAccessmodFile(input: $input) {
                    success
                  }
                }
            """,
            {"input": {"id": str(file.id)}},
        )
        self.assertEqual(True, r["data"]["deleteAccessmodFile"]["success"])
        self.assertEqual(False, File.objects.filter(id=file.id).exists())
        fileset.refresh_from_db()
        self.assertGreater(fileset.updated_at, original_fileset_updated_at)
