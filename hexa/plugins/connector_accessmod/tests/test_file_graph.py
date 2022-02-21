from django.conf import settings
from moto import mock_s3, mock_sts

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    File,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
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
        cls.SAMPLE_PROJECT_1 = Project.objects.create(
            name="Sample project 1",
            country="BE",
            owner=cls.USER_1,
            spatial_resolution=100,
        )
        cls.SAMPLE_PROJECT_2 = Project.objects.create(
            name="Sample project 2",
            country="BE",
            owner=cls.USER_1,
            spatial_resolution=100,
        )
        cls.LAND_COVER_ROLE = FilesetRole.objects.create(
            name="Land Cover",
            code=FilesetRoleCode.LAND_COVER,
            format=FilesetFormat.RASTER,
        )
        cls.BARRIER_ROLE = FilesetRole.objects.create(
            name="Barriers", code=FilesetRoleCode.BARRIER, format=FilesetFormat.RASTER
        )
        cls.SAMPLE_FILESET_1 = Fileset.objects.create(
            name="A cool fileset",
            role=cls.LAND_COVER_ROLE,
            project=cls.SAMPLE_PROJECT_1,
            owner=cls.USER_1,
        )
        cls.SAMPLE_FILESET_2 = Fileset.objects.create(
            name="Another nice fileset",
            role=cls.BARRIER_ROLE,
            project=cls.SAMPLE_PROJECT_1,
            owner=cls.USER_1,
        )
        cls.SAMPLE_FILESET_3 = Fileset.objects.create(
            name="And yet another fileset",
            role=cls.LAND_COVER_ROLE,
            project=cls.SAMPLE_PROJECT_2,
            owner=cls.USER_1,
        )
        cls.SAMPLE_FILE_1 = File.objects.create(
            fileset=cls.SAMPLE_FILESET_1, uri="afile.csv", mime_type="text/csv"
        )
        cls.SAMPLE_FILE_2 = File.objects.create(
            fileset=cls.SAMPLE_FILESET_1, uri="anotherfile.csv", mime_type="text/csv"
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
            {"id": str(self.SAMPLE_FILESET_1.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFileset"],
            {
                "id": str(self.SAMPLE_FILESET_1.id),
                "name": self.SAMPLE_FILESET_1.name,
                "role": {"id": str(self.SAMPLE_FILESET_1.role_id)},
                "owner": {"id": str(self.SAMPLE_FILESET_1.owner_id)},
                "files": [
                    {"id": str(f.id), "mimeType": f.mime_type, "uri": f.uri}
                    for f in self.SAMPLE_FILESET_1.file_set.all()
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
            {"id": str(self.SAMPLE_FILESET_1.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFileset"],
            None,
        )

    def test_accessmod_filesets(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!) {
                  accessmodFilesets(projectId: $projectId) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
            {"projectId": str(self.SAMPLE_PROJECT_1.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.SAMPLE_FILESET_2.id)},
                    {"id": str(self.SAMPLE_FILESET_1.id)},
                ],
            },
        )

    def test_accessmod_filesets_by_role(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!, $roleId: String!) {
                  accessmodFilesets(projectId: $projectId, roleId: $roleId) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                      role {
                        code
                      }
                    }
                  }
                }
            """,
            {
                "projectId": str(self.SAMPLE_PROJECT_1.id),
                "roleId": str(self.BARRIER_ROLE.id),
            },
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {
                        "id": str(self.SAMPLE_FILESET_2.id),
                        "role": {"code": self.BARRIER_ROLE.code},
                    },
                ],
            },
        )

    def test_accessmod_filesets_by_term(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!, $term: String!) {
                  accessmodFilesets(projectId: $projectId, term: $term) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
            {
                "projectId": str(self.SAMPLE_PROJECT_1.id),
                "term": "cool",
            },
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 1,
                "items": [
                    {
                        "id": str(self.SAMPLE_FILESET_1.id),
                    },
                ],
            },
        )

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!, $term: String!) {
                  accessmodFilesets(projectId: $projectId, term: $term) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
            {
                "projectId": str(self.SAMPLE_PROJECT_1.id),
                "term": "awesome",
            },
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

    def test_accessmod_filesets_pagination(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!) {
                  accessmodFilesets(projectId: $projectId, page: 1, perPage: 10) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
            {"projectId": str(self.SAMPLE_PROJECT_1.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.SAMPLE_FILESET_2.id)},
                    {"id": str(self.SAMPLE_FILESET_1.id)},
                ],
            },
        )

    def test_accessmod_filesets_empty(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!) {
                  accessmodFilesets(projectId: $projectId) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
            {"projectId": str(self.SAMPLE_PROJECT_1.id)},
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
                    "name": "A nice land cover file",
                    "projectId": str(self.SAMPLE_PROJECT_1.id),
                    "roleId": str(self.LAND_COVER_ROLE.id),
                }
            },
        )
        self.assertEqual(True, r1["data"]["createAccessmodFileset"]["success"])
        self.assertEqual(
            "A nice land cover file",
            r1["data"]["createAccessmodFileset"]["fileset"]["name"],
        )
        self.assertEqual(
            {"id": str(self.LAND_COVER_ROLE.id)},
            r1["data"]["createAccessmodFileset"]["fileset"]["role"],
        )
        fileset_id = r1["data"]["createAccessmodFileset"]["fileset"]["id"]

        r2 = self.run_query(
            """
                mutation prepareAccessmodFileUpload($input: PrepareAccessmodFileUploadInput) {
                  prepareAccessmodFileUpload(input: $input) {
                    success
                    uploadUrl
                    fileUri
                  }
                }
            """,
            {
                "input": {
                    "filesetId": fileset_id,
                    "mimeType": "text/csv",
                }
            },
        )

        self.assertEqual(
            r2["data"]["prepareAccessmodFileUpload"]["success"],
            True,
        )
        self.assertTrue(
            r2["data"]["prepareAccessmodFileUpload"]["uploadUrl"].startswith("https://")
        )
        self.assertIn(
            str(self.SAMPLE_PROJECT_1.id),
            r2["data"]["prepareAccessmodFileUpload"]["uploadUrl"],
        )
        self.assertIn(
            "X-Amz-SignedHeaders", r2["data"]["prepareAccessmodFileUpload"]["uploadUrl"]
        )
        self.assertTrue(
            r2["data"]["prepareAccessmodFileUpload"]["fileUri"].startswith("s3://")
        )
        self.assertTrue(
            r2["data"]["prepareAccessmodFileUpload"]["fileUri"].endswith(".csv")
        )
        self.assertIn(
            str(self.SAMPLE_PROJECT_1.id),
            r2["data"]["prepareAccessmodFileUpload"]["fileUri"],
        )
        file_uri = r2["data"]["prepareAccessmodFileUpload"]["fileUri"]

        r3 = self.run_query(
            """
                mutation createAccessmodFile($input: CreateAccessmodFileInput) {
                    createAccessmodFile(input: $input) {
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
        self.assertEqual(True, r3["data"]["createAccessmodFile"]["success"])
        self.assertEqual(file_uri, r3["data"]["createAccessmodFile"]["file"]["uri"])
        self.assertEqual(
            "text/csv", r3["data"]["createAccessmodFile"]["file"]["mimeType"]
        )
        self.assertEqual(
            fileset_id, r3["data"]["createAccessmodFile"]["file"]["fileset"]["id"]
        )
        file_id = r3["data"]["createAccessmodFile"]["file"]["id"]

        # The fileset updated_at value should be equal to the created_at of the most recent file
        fileset = Fileset.objects.get(id=fileset_id)
        file = File.objects.get(id=file_id)
        self.assertGreater(fileset.updated_at, file.created_at)

    def test_delete_fileset(self):
        self.client.force_login(self.USER_1)
        fileset = Fileset.objects.create(
            name="About to be deleted",
            role=self.LAND_COVER_ROLE,
            project=self.SAMPLE_PROJECT_1,
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
            role=self.LAND_COVER_ROLE,
            project=self.SAMPLE_PROJECT_1,
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

    def test_accessmod_fileset_role(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFilesetRole($id: String!) {
                  accessmodFilesetRole(id: $id) {
                    id
                    code
                    name
                    format
                  }
                }
            """,
            {"id": str(self.LAND_COVER_ROLE.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFilesetRole"],
            {
                "id": str(self.LAND_COVER_ROLE.id),
                "code": self.LAND_COVER_ROLE.code,
                "name": self.LAND_COVER_ROLE.name,
                "format": self.LAND_COVER_ROLE.format,
            },
        )

    def test_accessmod_fileset_roles(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodFilesetRoles {
                  accessmodFilesetRoles {
                    id
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodFilesetRoles"],
            [
                {"id": str(self.BARRIER_ROLE.id)},
                {"id": str(self.LAND_COVER_ROLE.id)},
            ],
        )
