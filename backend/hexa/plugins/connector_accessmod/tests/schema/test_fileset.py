import uuid

from django.conf import settings
from django.test import override_settings
from moto import mock_aws

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    File,
    Fileset,
    FilesetMode,
    FilesetRole,
    FilesetRoleCode,
    FilesetStatus,
    Project,
    ProjectPermission,
)
from hexa.plugins.connector_s3.models import Bucket
from hexa.plugins.connector_s3.tests.mocks.s3_credentials_mock import get_s3_mocked_env
from hexa.user_management.models import PermissionMode, User


@override_settings(**get_s3_mocked_env())
class FilesetTest(GraphQLTestCase):
    USER_GREG = None
    PROJECT_BORING = None
    PROJECT_EXCITING = None
    LAND_COVER_ROLE = None
    BARRIER_ROLE = None
    FILESET_COOL = None
    FILESET_NICE = None
    FILESET_ANOTHER = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_GREG = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimrocks",
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janesthebest",
        )
        cls.PROJECT_BORING = Project.objects.create(
            name="Sample project 1",
            country="BE",
            author=cls.USER_GREG,
            spatial_resolution=100,
            crs=4326,
        )
        ProjectPermission.objects.create(
            project=cls.PROJECT_BORING, user=cls.USER_GREG, mode=PermissionMode.OWNER
        )
        cls.PROJECT_EXCITING = Project.objects.create(
            name="Sample project 2",
            country="BE",
            author=cls.USER_GREG,
            spatial_resolution=100,
            crs=4326,
        )
        cls.LAND_COVER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.LAND_COVER,
        )
        cls.BARRIER_ROLE = FilesetRole.objects.get(code=FilesetRoleCode.BARRIER)
        cls.FILESET_COOL = Fileset.objects.create(
            name="A cool fileset",
            status=FilesetStatus.VALID,
            role=cls.LAND_COVER_ROLE,
            project=cls.PROJECT_BORING,
            author=cls.USER_GREG,
            metadata={"foo": "bar"},
        )
        cls.FILESET_NICE = Fileset.objects.create(
            name="A nice automatic fileset",
            role=cls.BARRIER_ROLE,
            project=cls.PROJECT_BORING,
            author=cls.USER_GREG,
            mode=FilesetMode.AUTOMATIC_ACQUISITION,
        )
        cls.FILESET_ANOTHER = Fileset.objects.create(
            name="And yet another fileset",
            role=cls.LAND_COVER_ROLE,
            project=cls.PROJECT_EXCITING,
            author=cls.USER_GREG,
        )
        cls.SAMPLE_FILE_1 = File.objects.create(
            fileset=cls.FILESET_COOL, uri="afile.csv", mime_type="text/csv"
        )
        cls.SAMPLE_FILE_2 = File.objects.create(
            fileset=cls.FILESET_COOL, uri="anotherfile.csv", mime_type="text/csv"
        )
        bucket_name = settings.ACCESSMOD_BUCKET_NAME.split("://")[1].rstrip("/")
        cls.BUCKET = Bucket.objects.create(name=bucket_name)

    def test_accessmod_fileset_author(self):
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                query accessmodFileset($id: String!) {
                  accessmodFileset(id: $id) {
                    id
                    name
                    mode
                    status
                    role {
                        id
                    }
                    author {
                        id
                    }
                    files {
                        id
                        mimeType
                        uri
                    }
                    metadata
                  }
                }
            """,
            {"id": str(self.FILESET_COOL.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFileset"],
            {
                "id": str(self.FILESET_COOL.id),
                "name": self.FILESET_COOL.name,
                "mode": self.FILESET_COOL.mode,
                "status": self.FILESET_COOL.status,
                "role": {"id": str(self.FILESET_COOL.role_id)},
                "author": {"id": str(self.FILESET_COOL.author_id)},
                "files": [
                    {"id": str(f.id), "mimeType": f.mime_type, "uri": f.uri}
                    for f in self.FILESET_COOL.file_set.all()
                ],
                "metadata": {"foo": "bar"},
            },
        )

    def test_accessmod_fileset_not_author(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodFileset($id: String!) {
                  accessmodFileset(id: $id) {
                    id
                  }
                }
            """,
            {"id": str(self.FILESET_COOL.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFileset"],
            None,
        )

    def test_accessmod_filesets(self):
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!) {
                  accessmodFilesets(projectId: $projectId) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                      status
                      metadata
                    }
                  }
                }
            """,
            {"projectId": str(self.PROJECT_BORING.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {
                        "id": str(self.FILESET_NICE.id),
                        "status": self.FILESET_NICE.status,
                        "metadata": {},
                    },
                    {
                        "id": str(self.FILESET_COOL.id),
                        "status": self.FILESET_COOL.status,
                        "metadata": {"foo": "bar"},
                    },
                ],
            },
        )

    def test_accessmod_filesets_by_role(self):
        self.client.force_login(self.USER_GREG)

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
                "projectId": str(self.PROJECT_BORING.id),
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
                        "id": str(self.FILESET_NICE.id),
                        "role": {"code": self.BARRIER_ROLE.code},
                    },
                ],
            },
        )

    def test_accessmod_filesets_by_term(self):
        self.client.force_login(self.USER_GREG)

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
                "projectId": str(self.PROJECT_BORING.id),
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
                        "id": str(self.FILESET_COOL.id),
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
                "projectId": str(self.PROJECT_BORING.id),
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

    def test_accessmod_filesets_by_mode(self):
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                query accessmodFilesets($projectId: String!, $mode: AccessmodFilesetMode!) {
                  accessmodFilesets(projectId: $projectId, mode: $mode) {
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
                "projectId": str(self.PROJECT_BORING.id),
                "mode": FilesetMode.AUTOMATIC_ACQUISITION,
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
                        "id": str(self.FILESET_NICE.id),
                    }
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
                "projectId": str(self.PROJECT_BORING.id),
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
        self.client.force_login(self.USER_GREG)

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
            {"projectId": str(self.PROJECT_BORING.id)},
        )

        self.assertEqual(
            r["data"]["accessmodFilesets"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.FILESET_NICE.id)},
                    {"id": str(self.FILESET_COOL.id)},
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
            {"projectId": str(self.PROJECT_BORING.id)},
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

    @mock_aws
    def test_full_accessmod_upload_workflow(self):
        self.client.force_login(self.USER_GREG)

        # Step 1: create fileset
        r1 = self.run_query(
            """
                mutation createAccessmodFileset($input: CreateAccessmodFilesetInput!) {
                  createAccessmodFileset(input: $input) {
                    success
                    fileset {
                        id
                        name
                        status
                        role {
                            id
                        }
                    }
                  }
                }
            """,
            {
                "input": {
                    "name": "A scary nâme!!!  😱",
                    "projectId": str(self.PROJECT_BORING.id),
                    "roleId": str(self.LAND_COVER_ROLE.id),
                }
            },
        )
        self.assertTrue(r1["data"]["createAccessmodFileset"]["success"])
        self.assertEqual(
            "A scary nâme!!!  😱",
            r1["data"]["createAccessmodFileset"]["fileset"]["name"],
        )
        self.assertEqual(
            FilesetStatus.PENDING,
            r1["data"]["createAccessmodFileset"]["fileset"]["status"],
        )
        self.assertEqual(
            {"id": str(self.LAND_COVER_ROLE.id)},
            r1["data"]["createAccessmodFileset"]["fileset"]["role"],
        )
        fileset_id = r1["data"]["createAccessmodFileset"]["fileset"]["id"]

        r2 = self.run_query(
            """
                mutation prepareAccessmodFileUpload($input: PrepareAccessmodFileUploadInput!) {
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
            str(self.PROJECT_BORING.id),
            r2["data"]["prepareAccessmodFileUpload"]["uploadUrl"],
        )
        self.assertIn(
            "X-Amz-SignedHeaders", r2["data"]["prepareAccessmodFileUpload"]["uploadUrl"]
        )
        self.assertTrue(
            r2["data"]["prepareAccessmodFileUpload"]["fileUri"].startswith("s3://")
        )
        self.assertIn(
            "a_scary_name.csv",
            r2["data"]["prepareAccessmodFileUpload"]["fileUri"],
        )
        self.assertIn(
            str(self.PROJECT_BORING.id),
            r2["data"]["prepareAccessmodFileUpload"]["fileUri"],
        )
        file_uri = r2["data"]["prepareAccessmodFileUpload"]["fileUri"]

        r3 = self.run_query(
            """
                mutation createAccessmodFile($input: CreateAccessmodFileInput!) {
                    createAccessmodFile(input: $input) {
                        success
                        file {
                            id
                            uri
                            name
                            mimeType
                            fileset {
                                id
                                status
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
        self.assertTrue(r3["data"]["createAccessmodFile"]["success"])
        self.assertEqual(file_uri, r3["data"]["createAccessmodFile"]["file"]["uri"])
        self.assertEqual(
            FilesetStatus.PENDING,
            r3["data"]["createAccessmodFile"]["file"]["fileset"]["status"],
        )
        self.assertEqual(
            "text/csv", r3["data"]["createAccessmodFile"]["file"]["mimeType"]
        )
        self.assertIn(
            "a_scary_name.csv",
            r3["data"]["createAccessmodFile"]["file"]["name"],
        )
        self.assertEqual(
            fileset_id, r3["data"]["createAccessmodFile"]["file"]["fileset"]["id"]
        )
        file_id = r3["data"]["createAccessmodFile"]["file"]["id"]

        # The fileset updated_at value should be equal to the created_at of the most recent file
        fileset = Fileset.objects.get(id=fileset_id)
        file = File.objects.get(id=file_id)
        self.assertGreater(fileset.updated_at, file.created_at)

        r4 = self.run_query(
            """
              mutation prepareAccessmodFileDownload($input: PrepareAccessmodFileDownloadInput!) {
                prepareAccessmodFileDownload(input: $input) {
                  success
                  downloadUrl
                }
              }
            """,
            {
                "input": {
                    "fileId": str(file.id),
                }
            },
        )
        self.assertTrue(r4["data"]["prepareAccessmodFileDownload"]["success"])
        self.assertIn(
            f"https://{self.BUCKET.name}.s3.amazonaws.com/{self.PROJECT_BORING.id}/{file.name}",
            r4["data"]["prepareAccessmodFileDownload"]["downloadUrl"],
        )
        self.assertIn(
            "X-Amz-SignedHeaders",
            r4["data"]["prepareAccessmodFileDownload"]["downloadUrl"],
        )

    def test_create_fileset_errors(self):
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                mutation createAccessmodFileset($input: CreateAccessmodFilesetInput!) {
                  createAccessmodFileset(input: $input) {
                    success
                    fileset {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "name": self.FILESET_COOL.name,
                    "projectId": str(self.PROJECT_BORING.id),
                    "roleId": str(self.LAND_COVER_ROLE.id),
                }
            },
        )
        self.assertEqual(
            {"success": False, "fileset": None, "errors": ["NAME_DUPLICATE"]},
            r["data"]["createAccessmodFileset"],
        )

    def test_update_fileset(self):
        self.client.force_login(self.USER_GREG)
        fileset = Fileset.objects.create(
            name="About to be deleted",
            role=self.LAND_COVER_ROLE,
            project=self.PROJECT_BORING,
            author=self.USER_GREG,
        )

        r = self.run_query(
            """
                mutation updateAccessmodFileset($input: UpdateAccessmodFilesetInput!) {
                  updateAccessmodFileset(input: $input) {
                    success
                    fileset {
                        name
                        metadata
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(fileset.id),
                    "name": "Updated name",
                    "metadata": {"yo": "lo"},
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "fileset": {
                    "name": "Updated name",
                    "metadata": {"yo": "lo"},
                },
            },
            r["data"]["updateAccessmodFileset"],
        )
        fileset.refresh_from_db()
        self.assertEqual(FilesetStatus.PENDING, fileset.status)

    def test_update_fileset_errors(self):
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                mutation updateAccessmodFileset($input: UpdateAccessmodFilesetInput!) {
                  updateAccessmodFileset(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {"input": {"id": str(uuid.uuid4())}},
        )
        self.assertEqual(
            {"success": False, "errors": ["NOT_FOUND"]},
            r["data"]["updateAccessmodFileset"],
        )

        fileset = Fileset.objects.create(
            name="Won't be updated because name is duplicated",
            role=self.LAND_COVER_ROLE,
            project=self.PROJECT_BORING,
            author=self.USER_GREG,
        )
        r = self.run_query(
            """
                mutation updateAccessmodFileset($input: UpdateAccessmodFilesetInput!) {
                  updateAccessmodFileset(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {"input": {"id": str(fileset.id), "name": self.FILESET_COOL.name}},
        )
        self.assertEqual(
            {"success": False, "errors": ["NAME_DUPLICATE"]},
            r["data"]["updateAccessmodFileset"],
        )

    def test_delete_fileset(self):
        self.client.force_login(self.USER_GREG)
        fileset = Fileset.objects.create(
            name="About to be deleted",
            role=self.LAND_COVER_ROLE,
            project=self.PROJECT_BORING,
            author=self.USER_GREG,
        )

        r = self.run_query(
            """
                mutation deleteAccessmodFileset($input: DeleteAccessmodFilesetInput!) {
                  deleteAccessmodFileset(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {"input": {"id": str(fileset.id)}},
        )
        self.assertEqual(
            {"success": True, "errors": []}, r["data"]["deleteAccessmodFileset"]
        )
        self.assertFalse(Fileset.objects.filter(id=fileset.id).exists())

    def test_delete_fileset_errors(self):
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                mutation deleteAccessmodFileset($input: DeleteAccessmodFilesetInput!) {
                  deleteAccessmodFileset(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {"input": {"id": str(uuid.uuid4())}},
        )
        self.assertEqual(
            {"success": False, "errors": ["NOT_FOUND"]},
            r["data"]["deleteAccessmodFileset"],
        )

        fileset = Fileset.objects.create(
            name="Won't be delete because used in analysis",
            role=self.LAND_COVER_ROLE,
            project=self.PROJECT_BORING,
            author=self.USER_GREG,
        )
        AccessibilityAnalysis.objects.create(
            author=self.USER_GREG,
            project=self.PROJECT_EXCITING,
            name="Annoying accessibility analysis",
            land_cover=fileset,
        )
        r = self.run_query(
            """
                mutation deleteAccessmodFileset($input: DeleteAccessmodFilesetInput!) {
                  deleteAccessmodFileset(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {"input": {"id": str(fileset.id)}},
        )
        self.assertEqual(
            {"success": False, "errors": ["FILESET_IN_USE"]},
            r["data"]["deleteAccessmodFileset"],
        )

    def test_create_file_errors(self):
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                mutation createAccessmodFile($input: CreateAccessmodFileInput!) {
                  createAccessmodFile(input: $input) {
                    success
                    file {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "uri": self.SAMPLE_FILE_1.uri,
                    "filesetId": str(self.FILESET_COOL.id),
                    "mimeType": "text/csv",
                }
            },
        )
        self.assertEqual(
            {"success": False, "file": None, "errors": ["URI_DUPLICATE"]},
            r["data"]["createAccessmodFile"],
        )

    def test_accessmod_fileset_role(self):
        self.client.force_login(self.USER_GREG)

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
        self.client.force_login(self.USER_GREG)

        r = self.run_query(
            """
                query accessmodFilesetRoles {
                  accessmodFilesetRoles {
                    id
                  }
                }
            """,
        )
        self.assertEqual(15, len(r["data"]["accessmodFilesetRoles"]))
        self.assertEqual(
            {"id": str(self.BARRIER_ROLE.id)},
            r["data"]["accessmodFilesetRoles"][0],
        )

    @mock_aws
    def test_prepare_fileset_visualization(self):
        self.client.force_login(self.USER_GREG)

        r1 = self.run_query(
            """
                mutation prepareFilesetVisualization($input: PrepareAccessmodFilesetVisualizationDownloadInput!) {
                  prepareAccessmodFilesetVisualizationDownload(input: $input) {
                    success
                    url
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.FILESET_COOL.id),
                }
            },
        )
        self.assertFalse(
            r1["data"]["prepareAccessmodFilesetVisualizationDownload"]["success"]
        )

        self.FILESET_COOL.visualization_uri = self.SAMPLE_FILE_1.uri
        self.FILESET_COOL.save()

        r2 = self.run_query(
            """
                mutation prepareFilesetVisualization($input: PrepareAccessmodFilesetVisualizationDownloadInput!) {
                  prepareAccessmodFilesetVisualizationDownload(input: $input) {
                    success
                    url
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.FILESET_COOL.id),
                }
            },
        )

        self.assertTrue(
            r2["data"]["prepareAccessmodFilesetVisualizationDownload"]["success"]
        )
        self.assertTrue(
            r2["data"]["prepareAccessmodFilesetVisualizationDownload"][
                "url"
            ].startswith("https://")
        )
