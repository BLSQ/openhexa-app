import hashlib
import json

from django.conf import settings

from hexa.datasets.models import (
    Dataset,
    DatasetFileSample,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.files import storage
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
    COLUMN_HASHES = {
        hashlib.md5(b"country").hexdigest(): "country",
        hashlib.md5(b"cases").hexdigest(): "cases",
    }

    def create_sample(self):
        return DatasetFileSample.objects.create(
            dataset_version_file=self.DATASET_FILE,
            sample=[{"country": "Belgium", "cases": 42}],
            status=DatasetFileSample.STATUS_FINISHED,
        )

    def set_properties(self):
        self.DATASET_FILE.properties = {
            "columns": self.COLUMN_HASHES,
            "column_order": list(self.COLUMN_HASHES),
        }
        self.DATASET_FILE.save()

    def set_profiling(self, column, **profile):
        column_hash = hashlib.md5(column.encode()).hexdigest()
        for key, value in profile.items():
            self.DATASET_FILE.update_or_create_attribute(
                key=f"{column_hash}.{key}", value=value, system=True
            )

    def preview(self):
        return preview_dataset_file(
            user=self.USER_ADMIN, file_id=str(self.DATASET_FILE.id)
        )

    def test_preview_dataset_file(self):
        result = self.preview()
        self.assertEqual(result["filename"], "test-file.csv")
        self.assertEqual(result["contentType"], "text/csv")

    def test_preview_dataset_file_not_found(self):
        result = preview_dataset_file(
            user=self.USER_ADMIN,
            file_id="00000000-0000-0000-0000-000000000000",
        )
        self.assertEqual(result, {"error": "Dataset file not found"})

    def test_preview_dataset_file_never_returns_sample_rows(self):
        self.create_sample()
        self.set_properties()

        result = self.preview()
        self.assertNotIn("fileSample", result)
        self.assertNotIn("Belgium", json.dumps(result))

    def test_preview_dataset_file_returns_columns_with_types(self):
        self.set_properties()
        self.set_profiling("country", data_type="string")
        self.set_profiling("cases", data_type="int64")

        result = self.preview()
        self.assertEqual(
            result["columns"],
            [
                {"name": "country", "type": "string"},
                {"name": "cases", "type": "int64"},
            ],
        )
        self.assertNotIn("properties", result)
        self.assertNotIn("attributes", result)

    def test_preview_dataset_file_leaves_out_profiling_statistics(self):
        self.set_properties()
        self.set_profiling("cases", data_type="int64", minimum=7, maximum=987654)

        result = self.preview()
        self.assertEqual(result["columns"][1], {"name": "cases", "type": "int64"})
        self.assertNotIn("987654", json.dumps(result))

    def test_preview_dataset_file_leaves_out_user_attributes(self):
        self.set_properties()
        self.DATASET_FILE.update_or_create_attribute(
            key="notes.data_type", value="patient names", system=False
        )

        self.assertNotIn("patient names", json.dumps(self.preview()))

    def test_preview_dataset_file_column_without_type(self):
        self.set_properties()

        result = self.preview()
        self.assertEqual(result["columns"][0], {"name": "country", "type": None})

    def test_preview_dataset_file_without_profiling(self):
        result = self.preview()
        self.assertIsNone(result["columns"])
        self.assertIsNone(result["profiling"])

    def test_preview_dataset_file_profiling_in_progress(self):
        DatasetFileSample.objects.create(
            dataset_version_file=self.DATASET_FILE,
            status=DatasetFileSample.STATUS_PROCESSING,
        )

        result = self.preview()
        self.assertIsNone(result["columns"])
        self.assertEqual(
            result["profiling"], {"status": "PROCESSING", "statusReason": None}
        )

    def test_preview_dataset_file_profiling_failed(self):
        DatasetFileSample.objects.create(
            dataset_version_file=self.DATASET_FILE,
            status=DatasetFileSample.STATUS_FAILED,
            status_reason="Unsupported file format",
        )

        result = self.preview()
        self.assertIsNone(result["columns"])
        self.assertEqual(
            result["profiling"],
            {"status": "FAILED", "statusReason": "Unsupported file format"},
        )


class CreateDatasetTest(MCPTestCase):
    FILES_JSON = json.dumps(
        [{"uri": "data.csv", "contentType": "text/csv", "content": "a,b\n1,2"}]
    )

    def test_create_dataset(self):
        result = create_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name="New Dataset",
            files_json=self.FILES_JSON,
            description="A new dataset",
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["dataset"]["name"], "New Dataset")

        dataset = Dataset.objects.get(slug=result["dataset"]["slug"])
        version = DatasetVersion.objects.get(dataset=dataset, name="v1")
        db_files = DatasetVersionFile.objects.filter(dataset_version=version)
        self.assertEqual(db_files.count(), 1)
        self.assertEqual(db_files.first().filename, "data.csv")
        self.assertEqual(db_files.first().content_type, "text/csv")

        full_uri = version.get_full_uri("data.csv")
        blob = storage.get_bucket_object(settings.WORKSPACE_DATASETS_BUCKET, full_uri)
        self.assertIsNotNone(blob)

    def test_create_dataset_no_access(self):
        result = create_dataset(
            user=self.USER_OUTSIDER,
            workspace_slug=self.WORKSPACE.slug,
            name="Unauthorized",
            files_json=self.FILES_JSON,
        )
        self.assertFalse(result["success"])

    def test_create_dataset_viewer_cannot_create(self):
        result = create_dataset(
            user=self.USER_VIEWER,
            workspace_slug=self.WORKSPACE.slug,
            name="Viewer Dataset",
            files_json=self.FILES_JSON,
        )
        self.assertFalse(result["success"])

    def test_create_dataset_invalid_files_json(self):
        result = create_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name="Bad Files",
            files_json="not valid json",
        )
        self.assertEqual(result, {"error": "Invalid JSON in files_json"})

    def test_create_dataset_empty_files_json(self):
        result = create_dataset(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name="Empty Files",
            files_json="[]",
        )
        self.assertEqual(
            result,
            {
                "error": "files_json must be a non-empty JSON array of {uri, contentType, content} objects"
            },
        )


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

    def test_create_dataset_version_with_files(self):
        files = [
            {"uri": "data.csv", "contentType": "text/csv", "content": "a,b\n1,2"},
            {
                "uri": "info.json",
                "contentType": "application/json",
                "content": '{"key": "value"}',
            },
        ]
        result = create_dataset_version(
            user=self.USER_ADMIN,
            dataset_id=str(self.DATASET.id),
            name="v2",
            changelog="Version with files",
            files_json=json.dumps(files),
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["version"]["name"], "v2")

        version = DatasetVersion.objects.get(id=result["version"]["id"])
        files_qs = DatasetVersionFile.objects.filter(dataset_version=version)
        self.assertEqual(files_qs.count(), 2)

        filenames = {f.filename for f in files_qs}
        self.assertEqual(filenames, {"data.csv", "info.json"})

        full_uri = version.get_full_uri("data.csv")
        blob = storage.get_bucket_object(settings.WORKSPACE_DATASETS_BUCKET, full_uri)
        self.assertIsNotNone(blob)

    def test_create_dataset_version_with_invalid_files_json(self):
        result = create_dataset_version(
            user=self.USER_ADMIN,
            dataset_id=str(self.DATASET.id),
            name="v3",
            files_json="not valid json",
        )
        self.assertEqual(result, {"error": "Invalid JSON in files_json"})
