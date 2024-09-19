import json
from io import BytesIO

from django.conf import settings
from django.db import IntegrityError

from hexa.core.test import GraphQLTestCase
from hexa.files import storage
from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembershipRole

from ..models import Dataset, DatasetFileMetadata, DatasetVersionFile
from .testutils import DatasetTestMixin


class DatasetTest(GraphQLTestCase, DatasetTestMixin):
    def test_create_dataset(self):
        superuser = self.create_user(
            "serena@blsq.org",
            is_superuser=True,
        )

        workspace = self.create_workspace(
            superuser,
            name="My Workspace",
            description="Test workspace",
        )

        self.client.force_login(superuser)
        r = self.run_query(
            """
            mutation CreateDataset ($input: CreateDatasetInput!) {
                createDataset(input: $input) {
                    dataset {
                        name
                        description
                        workspace {
                            slug
                        }
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": workspace.slug,
                    "name": "My dataset",
                    "description": "Description of dataset",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "dataset": {
                    "name": "My dataset",
                    "description": "Description of dataset",
                    "workspace": {"slug": workspace.slug},
                },
            },
            r["data"]["createDataset"],
        )

    def test_create_dataset_unauthorized(self):
        superuser = self.create_user(
            "serena@blsq.org",
            is_superuser=True,
        )
        non_workspace_member = self.create_user("user@blsq.org")

        workspace = self.create_workspace(
            superuser,
            name="My Workspace",
            description="Test workspace",
        )

        self.client.force_login(non_workspace_member)
        r = self.run_query(
            """
            mutation CreateDataset ($input: CreateDatasetInput!) {
                createDataset(input: $input) {
                    dataset {
                        id
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": workspace.slug,
                    "name": "My dataset",
                    "description": "Description of dataset",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["WORKSPACE_NOT_FOUND"],
                "dataset": None,
            },
            r["data"]["createDataset"],
        )

    def test_create_dataset_by_viewer(self):
        superuser = self.create_user(
            "serena@blsq.org",
            is_superuser=True,
        )

        workspace = self.create_workspace(
            superuser,
            name="My Workspace",
            description="Test workspace",
        )

        viewer = self.create_user("user@blsq.org")
        self.join_workspace(viewer, workspace, WorkspaceMembershipRole.VIEWER)

        self.client.force_login(viewer)
        r = self.run_query(
            """
            mutation CreateDataset ($input: CreateDatasetInput!) {
                createDataset(input: $input) {
                    dataset {
                        id
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": workspace.slug,
                    "name": "My dataset",
                    "description": "Description of dataset",
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "dataset": None,
            },
            r["data"]["createDataset"],
        )

    def test_update_dataset(self):
        superuser = self.create_user("superuser@blsq.com", is_superuser=True)
        user = self.create_user("user@blsq.com")
        workspace = self.create_workspace(superuser, "My Workspace", "Test workspace")
        membership = self.join_workspace(
            user, workspace, WorkspaceMembershipRole.VIEWER
        )

        dataset = self.create_dataset(
            superuser, workspace, "My dataset", "Description of dataset"
        )
        self.client.force_login(user)
        self.run_query(
            """
            mutation UpdateDataset ($input: UpdateDatasetInput!) {
                updateDataset(input: $input) {
                    dataset {
                        name
                        description
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "datasetId": str(dataset.id),
                    "name": "My dataset updated",
                    "description": "Description of dataset updated",
                }
            },
        )
        # Viewer cannot update dataset
        dataset.refresh_from_db()
        self.assertEqual(dataset.name, "My dataset")
        self.assertEqual(dataset.description, "Description of dataset")

        # Editor can update dataset
        membership.role = WorkspaceMembershipRole.EDITOR
        membership.save()

        self.run_query(
            """
            mutation UpdateDataset ($input: UpdateDatasetInput!) {
                updateDataset(input: $input) {
                    dataset {
                        name
                        description
                    }
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "datasetId": str(dataset.id),
                    "name": "My dataset updated",
                    "description": "Description of dataset updated",
                }
            },
        )
        dataset.refresh_from_db()
        self.assertEqual(dataset.name, "My dataset updated")
        self.assertEqual(dataset.description, "Description of dataset updated")

    def test_delete_dataset(self):
        superuser = self.create_user("superuser@blsq.com", is_superuser=True)
        user = self.create_user("user@blsq.com")
        workspace = self.create_workspace(superuser, "My Workspace", "Test workspace")
        membership = self.join_workspace(
            user, workspace, WorkspaceMembershipRole.VIEWER
        )

        dataset = self.create_dataset(
            superuser, workspace, "My dataset", "Description of dataset"
        )
        self.client.force_login(user)
        r = self.run_query(
            """
            mutation DeleteDataset ($input: DeleteDatasetInput!) {
                deleteDataset(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(dataset.id),
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deleteDataset"],
        )

        membership.role = WorkspaceMembershipRole.EDITOR
        membership.save()
        r = self.run_query(
            """
            mutation DeleteDataset ($input: DeleteDatasetInput!) {
                deleteDataset(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(dataset.id),
                }
            },
        )
        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteDataset"],
        )
        self.assertFalse(Dataset.objects.filter(id=dataset.id).exists())

    def test_workspace_datasets(self):
        superuser = self.create_user("superuser@blsq.com", is_superuser=True)
        user = self.create_user("user@blsq.com")
        workspace = self.create_workspace(superuser, "My Workspace", "Test workspace")
        self.join_workspace(user, workspace, WorkspaceMembershipRole.VIEWER)

        dataset_1 = self.create_dataset(
            superuser, workspace, "My dataset", "Description of dataset"
        )
        dataset_2 = self.create_dataset(
            superuser, workspace, "My dataset 2", "Description of dataset 2"
        )

        self.client.force_login(user)
        r = self.run_query(
            """
            query WorkspaceDatasets ($workspaceSlug: String!) {
                workspace (slug: $workspaceSlug) {
                    datasets {
                        items {
                            dataset {
                                id
                            }
                        }
                        
                    }
                }
            }
            """,
            {"workspaceSlug": workspace.slug},
        )

        self.assertEqual(
            {
                "workspace": {
                    "datasets": {
                        "items": [
                            {"dataset": {"id": str(dataset_2.id)}},
                            {"dataset": {"id": str(dataset_1.id)}},
                        ]
                    }
                }
            },
            r["data"],
        )


class DatasetVersionTest(GraphQLTestCase, DatasetTestMixin):
    @classmethod
    def setUpTestData(cls):
        storage.reset()
        storage.create_bucket(settings.WORKSPACE_DATASETS_BUCKET)

    def test_create_dataset_version(self):
        superuser = self.create_user("superuser@blsq.com", is_superuser=True)

        workspace = self.create_workspace(superuser, "Workspace", "Description")
        dataset = self.create_dataset(
            superuser, workspace, "Dataset", "Dataset's description"
        )

        self.client.force_login(superuser)
        r = self.run_query(
            """
            mutation CreateDatasetVersion ($input: CreateDatasetVersionInput!) {
                createDatasetVersion(input: $input) {
                    success
                    errors
                    version {
                        name
                        description
                    }
                }
            }
                """,
            {
                "input": {
                    "datasetId": str(dataset.id),
                    "name": "Version 1",
                    "description": "Version 1 description",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "version": {
                    "name": "Version 1",
                    "description": "Version 1 description",
                },
            },
            r["data"]["createDatasetVersion"],
        )

    def test_create_duplicate(self):
        self.test_create_dataset_version()
        superuser = User.objects.get(email="superuser@blsq.com")
        dataset = Dataset.objects.get(name="Dataset")
        with self.assertRaises(IntegrityError):
            dataset.create_version(principal=superuser, name="Version 1")

    def test_generate_upload_url(self):
        superuser = self.create_user("superuser@blsq.com", is_superuser=True)
        workspace = self.create_workspace(
            superuser,
            name="My Workspace",
            description="Test workspace",
        )
        dataset = self.create_dataset(
            superuser, workspace, "Dataset", "Dataset description"
        )
        dataset_version = self.create_dataset_version(superuser, dataset=dataset)
        self.client.force_login(superuser)
        r = self.run_query(
            """
            mutation generateDatasetUploadUrl ($input: GenerateDatasetUploadUrlInput!) {
                generateDatasetUploadUrl(input: $input) {
                    uploadUrl
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "versionId": str(dataset_version.id),
                    "uri": "uri_file.csv",
                    "contentType": "text/csv",
                }
            },
        )
        self.assertEqual(
            r["data"]["generateDatasetUploadUrl"],
            {
                "uploadUrl": f"http://mockstorage.com/{settings.WORKSPACE_DATASETS_BUCKET}/{str(dataset.id)}/{str(dataset_version.id)}/uri_file.csv/upload",
                "success": True,
                "errors": [],
            },
        )

    def test_get_file_by_name(self):
        self.test_create_dataset_version()
        superuser = User.objects.get(email="superuser@blsq.com")
        dataset = Dataset.objects.get(name="Dataset")
        self.client.force_login(superuser)

        r = self.run_query(
            """
            query getFileByName($versionId: ID!, $name: String!) {
                datasetVersion(id: $versionId) {
                    fileByName(name: $name) {
                        filename
                    }
                }
            }
        """,
            {"versionId": str(dataset.latest_version.id), "name": "file.csv"},
        )

        self.assertEqual({"datasetVersion": {"fileByName": None}}, r["data"])

        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=superuser,
        )

        r = self.run_query(
            """
            query getFileByName($versionId: ID!, $name: String!) {
                datasetVersion(id: $versionId) {
                    fileByName(name: $name) {
                        filename
                    }
                }
            }
        """,
            {"versionId": str(dataset.latest_version.id), "name": "file.csv"},
        )

        self.assertEqual(
            {"datasetVersion": {"fileByName": {"filename": file.filename}}}, r["data"]
        )

    def test_get_file_metadata(self):
        self.test_create_dataset_version()
        superuser = User.objects.get(email="superuser@blsq.com")
        dataset = Dataset.objects.get(name="Dataset")
        self.client.force_login(superuser)
        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=superuser,
        )
        metadata = DatasetFileMetadata.objects.create(
            dataset_version_file=file,
            sample=json.dumps({"key": "value"}),
            status=DatasetFileMetadata.STATUS_PROCESSING,
        )
        r = self.run_query(
            """
                    query GetDatasetVersionFile($id: ID!) {
                      datasetVersionFile(id: $id) {
                        filename
                        fileMetadata {
                          status
                          sample
                        }
                      }
                    }
        """,
            {"id": str(file.id)},
        )
        self.assertEqual(
            {
                "datasetVersionFile": {
                    "filename": file.filename,
                    "fileMetadata": {
                        "status": metadata.status,
                        "sample": metadata.sample,
                    },
                }
            },
            r["data"],
        )

    def test_prepare_version_file_download(self):
        serena = self.create_user("sereba@blsq.org", is_superuser=True)
        workspace = self.create_workspace(
            serena,
            name="My Workspace",
            description="Test workspace",
        )

        olivia = self.create_user(
            "olivia@blsq.org",
        )
        self.join_workspace(
            olivia, workspace=workspace, role=WorkspaceMembershipRole.ADMIN
        )

        robert = self.create_user(
            "robert@blsq.org",
        )
        self.join_workspace(
            robert, workspace=workspace, role=WorkspaceMembershipRole.VIEWER
        )

        dataset = self.create_dataset(
            olivia, workspace, "Dataset", "Dataset description"
        )
        dataset_version = self.create_dataset_version(olivia, dataset=dataset)
        version_file = self.create_dataset_version_file(
            olivia, dataset_version=dataset_version
        )
        storage.save_object(
            settings.WORKSPACE_DATASETS_BUCKET,
            version_file.uri,
            BytesIO(b"some content"),
        )

        for user in [robert, olivia]:
            self.client.force_login(user)
            r = self.run_query(
                """
                mutation PrepareVersionFileDownload ($input: PrepareVersionFileDownloadInput!) {
                    prepareVersionFileDownload(input: $input) {
                        downloadUrl
                        success
                        errors
                    }
                }
                """,
                {
                    "input": {
                        "fileId": str(version_file.id),
                    }
                },
            )
            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "downloadUrl": f"http://mockstorage.com/{settings.WORKSPACE_DATASETS_BUCKET}/{version_file.uri}",
                },
                r["data"]["prepareVersionFileDownload"],
            )

    def test_prepare_version_file_download_linked_dataset(self):
        serena = self.create_user("sereba@blsq.org", is_superuser=True)
        src_workspace = self.create_workspace(
            serena,
            name="Source Workspace",
            description="Test workspace",
        )

        dataset = self.create_dataset(
            serena, src_workspace, "Dataset", "Dataset description"
        )
        dataset_version = self.create_dataset_version(serena, dataset=dataset)
        version_file = self.create_dataset_version_file(
            serena, dataset_version=dataset_version
        )
        storage.save_object(
            settings.WORKSPACE_DATASETS_BUCKET,
            version_file.uri,
            BytesIO(b"some content"),
        )

        tgt_workspace = self.create_workspace(
            serena, "Target Workspace", "Test workspace"
        )
        olivia = self.create_user(
            "olivia@blsq.org",
        )
        self.join_workspace(
            olivia, workspace=tgt_workspace, role=WorkspaceMembershipRole.ADMIN
        )

        self.client.force_login(olivia)
        r = self.run_query(
            """
            mutation PrepareVersionFileDownload ($input: PrepareVersionFileDownloadInput!) {
                prepareVersionFileDownload(input: $input) {
                    downloadUrl
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "fileId": str(version_file.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["FILE_NOT_FOUND"],
                "downloadUrl": None,
            },
            r["data"]["prepareVersionFileDownload"],
        )
        dataset.link(principal=olivia, workspace=tgt_workspace)

        r = self.run_query(
            """
            mutation PrepareVersionFileDownload ($input: PrepareVersionFileDownloadInput!) {
                prepareVersionFileDownload(input: $input) {
                    downloadUrl
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "fileId": str(version_file.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "downloadUrl": f"http://mockstorage.com/{settings.WORKSPACE_DATASETS_BUCKET}/{version_file.uri}",
            },
            r["data"]["prepareVersionFileDownload"],
        )
