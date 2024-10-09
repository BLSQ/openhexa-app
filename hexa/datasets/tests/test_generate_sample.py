import os
from unittest.mock import patch

from django.test import override_settings
from pandas.errors import EmptyDataError

from hexa.core.test import TestCase
from hexa.datasets.models import Dataset, DatasetFileSample, DatasetVersionFile
from hexa.datasets.queue import add_system_attributes, generate_sample, load_df
from hexa.files import storage
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class TestCreateDatasetFileSampleTask(TestCase):
    @classmethod
    def setUpTestData(cls):
        storage.reset()
        cls.USER_SERENA = User.objects.create_user(
            "serena@bluesquarehub.com", "serena's password", is_superuser=True
        )
        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SERENA, name="My Workspace", description="Test workspace"
        )

        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_SERENA,
            cls.WORKSPACE,
            name="Dataset",
            description="Dataset's description",
        )
        cls.DATASET_VERSION = cls.DATASET.create_version(
            principal=cls.USER_SERENA, name="v1"
        )

    @override_settings(WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE=3)
    def test_generate_sample(
        self,
    ):
        CASES = [
            (
                "example_names.csv",
                DatasetFileSample.STATUS_FINISHED,
                [
                    {"name": "Jack", "surname": "Howard"},
                    {"name": "Olivia", "surname": "Brown"},
                    {"name": "Lily", "surname": "Evans"},
                ],
                None,
            ),
            # The CSV only contains 2 lines so it's going to add existing lines to achieve the desired sample size
            (
                "example_names_2_lines.csv",
                DatasetFileSample.STATUS_FINISHED,
                [
                    {"name": "Liam", "surname": "Smith"},
                    {"name": "Joe", "surname": "Doe"},
                    {"name": "Joe", "surname": "Doe"},
                ],
                None,
            ),
            (
                "example_names_0_lines.csv",
                DatasetFileSample.STATUS_FINISHED,
                [],
                None,
            ),
            (
                "example_names.parquet",
                DatasetFileSample.STATUS_FINISHED,
                [
                    {"name": "Jack", "surname": "Howard"},
                    {"name": "Olivia", "surname": "Brown"},
                    {"name": "Lily", "surname": "Evans"},
                ],
                None,
            ),
            (
                "example_names.xlsx",
                DatasetFileSample.STATUS_FINISHED,
                [
                    {"name": "Jack", "surname": "Howard"},
                    {"name": "Olivia", "surname": "Brown"},
                    {"name": "Lily", "surname": "Evans"},
                ],
                None,
            ),
        ]
        for (
            fixture_name,
            expected_status,
            expected_sample,
            expected_status_reason,
        ) in CASES:
            with self.subTest(fixture_name=fixture_name):
                fixture_file_path = os.path.join(
                    os.path.dirname(__file__), f"./fixtures/{fixture_name}"
                )
                version_file = DatasetVersionFile.objects.create_if_has_perm(
                    self.USER_SERENA,
                    self.DATASET_VERSION,
                    uri=fixture_file_path,
                    content_type="application/octet-stream",
                )

                with patch(
                    "hexa.datasets.queue.generate_download_url"
                ) as mock_generate_download_url:
                    mock_generate_download_url.return_value = fixture_file_path
                    df = load_df(version_file)
                    sample_entry = generate_sample(version_file, df)
                    self.assertEqual(sample_entry.status, expected_status)
                    self.assertEqual(sample_entry.sample, expected_sample)

                    if expected_status_reason:
                        self.assertEqual(
                            sample_entry.status_reason, expected_status_reason
                        )

    def test_generate_sample_fails(self):
        fixture_name = "example_empty_file.csv"
        fixture_file_path = os.path.join(
            os.path.dirname(__file__), f"fixtures/{fixture_name}"
        )
        version_file = DatasetVersionFile.objects.create_if_has_perm(
            self.USER_SERENA,
            self.DATASET_VERSION,
            uri=fixture_file_path,
            content_type="application/octet-stream",
        )

        with patch(
            "hexa.datasets.queue.generate_download_url"
        ) as mock_generate_download_url:
            mock_generate_download_url.return_value = fixture_file_path

            with self.assertRaises(EmptyDataError):
                load_df(version_file)

    @override_settings(WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE=3)
    def test_add_system_attributes(self):
        fixture_name = "example_names.csv"
        fixture_file_path = os.path.join(
            os.path.dirname(__file__), f"./fixtures/{fixture_name}"
        )
        version_file = DatasetVersionFile.objects.create_if_has_perm(
            self.USER_SERENA,
            self.DATASET_VERSION,
            uri=fixture_file_path,
            content_type="application/octet-stream",
        )

        with patch(
            "hexa.datasets.queue.generate_download_url"
        ) as mock_generate_download_url:
            mock_generate_download_url.return_value = fixture_file_path
            df = load_df(version_file)
            add_system_attributes(version_file, df)

            # Check if attributes are added correctly
            attributes = version_file.attributes.all()
            for attr in attributes:
                print(attr)
            self.assertTrue(
                any(
                    attr.key == "c3VybmFtZQ==.data_type" and attr.value == "string"
                    for attr in attributes
                )
            )
            self.assertTrue(
                any(
                    attr.key == "c3VybmFtZQ==.missing_values" and attr.value == 0
                    for attr in attributes
                )
            )
