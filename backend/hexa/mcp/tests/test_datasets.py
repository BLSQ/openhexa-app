from hexa.datasets.models import Dataset, DatasetVersion
from hexa.mcp.tools.datasets import (
    create_dataset,
    create_dataset_version,
    get_dataset,
    list_datasets,
    preview_dataset_file,
)

from .testutils import MCPTestCase


class ListDatasetsTest(MCPTestCase):
    def test_list_datasets(self):
        result = list_datasets(user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug)
        datasets = result["datasets"]
        self.assertEqual(datasets["totalItems"], 1)
        self.assertEqual(datasets["items"][0]["name"], "Test Dataset")

    def test_list_datasets_workspace_not_found(self):
        result = list_datasets(user=self.USER_ADMIN, workspace_slug="nonexistent")
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_list_datasets_no_access(self):
        result = list_datasets(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result, {"error": "Workspace not found"})

    def test_list_datasets_viewer(self):
        result = list_datasets(
            user=self.USER_VIEWER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result["datasets"]["totalItems"], 1)


class GetDatasetTest(MCPTestCase):
    def test_get_dataset(self):
        result = get_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            dataset_slug=self.DATASET.slug,
        )
        self.assertEqual(result["name"], "Test Dataset")
        self.assertEqual(result["description"], "A test dataset")

    def test_get_dataset_includes_versions(self):
        result = get_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            dataset_slug=self.DATASET.slug,
        )
        self.assertIn("versions", result)
        self.assertEqual(result["versions"]["totalItems"], 1)
        self.assertEqual(result["versions"]["items"][0]["name"], "v1")

    def test_get_dataset_includes_latest_version_files(self):
        result = get_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            dataset_slug=self.DATASET.slug,
        )
        self.assertIn("latestVersion", result)
        latest = result["latestVersion"]
        self.assertIsNotNone(latest)
        self.assertEqual(latest["files"]["totalItems"], 1)
        self.assertEqual(latest["files"]["items"][0]["filename"], "test-file.csv")

    def test_get_dataset_not_found(self):
        result = get_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            dataset_slug="nonexistent",
        )
        self.assertEqual(result, {"error": "Dataset not found"})

    def test_get_dataset_no_access(self):
        result = get_dataset(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            dataset_slug=self.DATASET.slug,
        )
        self.assertEqual(result, {"error": "Dataset not found"})


class PreviewDatasetFileTest(MCPTestCase):
    def test_preview_dataset_file(self):
        result = preview_dataset_file(
            user=self.USER_ADMIN, file_id=str(self.DATASET_FILE.id)
        )
        self.assertEqual(result["filename"], "test-file.csv")
        self.assertEqual(result["contentType"], "text/csv")
        self.assertIn("fileSample", result)

    def test_preview_dataset_file_not_found(self):
        result = preview_dataset_file(
            user=self.USER_ADMIN,
            file_id="00000000-0000-0000-0000-000000000000",
        )
        self.assertEqual(result, {"error": "Dataset file not found"})


class CreateDatasetTest(MCPTestCase):
    def test_create_dataset(self):
        result = create_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name="New Dataset",
            description="A new dataset",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["dataset"]["name"], "New Dataset")
        self.assertTrue(Dataset.objects.filter(slug=result["dataset"]["slug"]).exists())

    def test_create_dataset_no_access(self):
        result = create_dataset(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            name="Unauthorized",
        )
        self.assertFalse(result["success"])

    def test_create_dataset_viewer_cannot_create(self):
        result = create_dataset(
            user=self.USER_VIEWER,
            workspace_slug=self.WORKSPACE.slug,
            name="Viewer Dataset",
        )
        self.assertFalse(result["success"])


class CreateDatasetVersionTest(MCPTestCase):
    def test_create_dataset_version(self):
        result = create_dataset_version(
            user=self.USER_ADMIN,
            dataset_id=str(self.DATASET.id),
            name="v2",
            changelog="Second version",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["version"]["name"], "v2")
        self.assertEqual(result["version"]["changelog"], "Second version")
        self.assertTrue(
            DatasetVersion.objects.filter(dataset=self.DATASET, name="v2").exists()
        )

    def test_create_dataset_version_duplicate_name(self):
        result = create_dataset_version(
            user=self.USER_ADMIN,
            dataset_id=str(self.DATASET.id),
            name="v1",
        )
        self.assertFalse(result["success"])
        self.assertIn("DUPLICATE_NAME", result["errors"])
