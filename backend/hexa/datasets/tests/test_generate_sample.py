import os
from unittest.mock import patch

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from pandas.errors import EmptyDataError

from hexa.core.test import TestCase
from hexa.datasets.models import (
    DataframeJsonEncoder,
    Dataset,
    DatasetFileSample,
    DatasetVersionFile,
)
from hexa.datasets.queue import (
    add_system_attributes,
    generate_profile,
    generate_sample,
    get_previous_version_file,
    load_df,
)
from hexa.datasets.tests.fixtures.wkb_geometry_encoded import wkb_geometry
from hexa.datasets.tests.testutils import DatasetTestMixin
from hexa.files import storage
from hexa.metadata.models import MetadataAttribute
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


class TestDataframeJsonEncoder(TestCase):
    def test_default(self):
        encoder = DataframeJsonEncoder()
        self.assertEqual(encoder.encode({"a": float("nan")}), '{"a": null}')


class TestCreateDatasetFileSampleTask(TestCase, DatasetTestMixin):
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
            (
                "example_uuid_dates.csv",
                DatasetFileSample.STATUS_FINISHED,
                [
                    {
                        "created_at": "2023-10-05T12:00:00Z",
                        "id": "5i1f1g0h-2g3h-8i7h-3d4e-5f6g7h8i9j0k",
                        "label": "Bos taurus",
                    },
                    {
                        "created_at": "2023-11-14T12:00:00Z",
                        "id": "5w1t1u0v-2u3v-8w7v-3r4s-5t6u7v8w9x0y",
                        "label": "Panthera leo bleyenberghi",
                    },
                    {
                        "created_at": "2023-10-01T12:00:00Z",
                        "id": "1e7b7e6e-8c9d-4f3e-9c1f-1a2b3c4d5e6f",
                        "label": "Panthera leo",
                    },
                ],
                None,
            ),
            (
                "example_with_nan.csv",
                DatasetFileSample.STATUS_FINISHED,
                [
                    {
                        "age": None,
                        "name": "Liam",
                        "married": False,
                        "surname": "Smith",
                    },
                    {"age": 10.0, "name": "Joe", "married": True, "surname": "Doe"},
                    {"age": 10.0, "name": "Joe", "married": True, "surname": "Doe"},
                ],
                None,
            ),
            (
                "example_with_byte.parquet",
                DatasetFileSample.STATUS_FINISHED,
                [
                    {
                        "geometry": "<SKIPPED_BYTES>",
                        "id": "2",
                        "name": "District B",
                        "value": 2.5,
                    },
                    {
                        "geometry": "<SKIPPED_BYTES>",
                        "id": "1",
                        "name": "District A",
                        "value": None,
                    },
                    {
                        "geometry": "<SKIPPED_BYTES>",
                        "id": "1",
                        "name": "District A",
                        "value": None,
                    },
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
                    os.path.dirname(__file__), "fixtures", fixture_name
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
                    generate_sample(version_file, df)
                    sample_entry = version_file.sample_entry
                    self.assertEqual(sample_entry.status, expected_status)
                    self.assertEqual(sample_entry.sample, expected_sample)

                    if expected_status_reason:
                        self.assertEqual(
                            sample_entry.status_reason, expected_status_reason
                        )

    @override_settings(WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE=1)
    def test_generate_sample_wkb(
        self,
    ):
        CASES = [
            (
                "example_with_wkb_geometry.parquet",
                DatasetFileSample.STATUS_FINISHED,
                [wkb_geometry],
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
                    os.path.dirname(__file__), "fixtures", fixture_name
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
                    generate_sample(version_file, df)
                    sample_entry = version_file.sample_entry
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

    def test_generate_profile(self):
        df = pd.DataFrame(
            {1234: [1, 2, 3, 4, 5], "str_column": ["a", "b", "c", "d", "e"]}
        )
        profile = generate_profile(df)
        self.assertEqual(
            profile,
            [
                {
                    "column_name": "1234",
                    "constant_values": False,
                    "count": 5,
                    "data_type": "int64",
                    "distinct_values": 5,
                    "missing_values": 0,
                    "unique_values": 5,
                },
                {
                    "column_name": "str_column",
                    "constant_values": False,
                    "count": 5,
                    "data_type": "string",
                    "distinct_values": 5,
                    "missing_values": 0,
                    "unique_values": 5,
                },
            ],
        )

    def test_add_system_attributes(self):
        CASES = [
            (
                "example_names_with_age.csv",
                [
                    "data_type",
                    "missing_values",
                    "unique_values",
                    "distinct_values",
                    "constant_values",
                ],
                "example_names_with_age_profiling.csv",
            ),
            (
                "senegal_rural_raw.csv",
                [
                    "data_type",
                    "missing_values",
                    "unique_values",
                    "distinct_values",
                    "constant_values",
                ],
                "senegal_rural_raw_profiling.csv",
            ),
        ]
        for case, expected_values, expected_result in CASES:
            with self.subTest(case=case):
                fixture_name = case
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
                    # Load expected results
                    expected_result_file_path = os.path.join(
                        os.path.dirname(__file__), f"./fixtures/{expected_result}"
                    )
                    expected_df = pd.read_csv(expected_result_file_path)

                    # Compare the values
                    for hashed_key, original_key in version_file.properties[
                        "columns"
                    ].items():
                        for value in expected_values:
                            attribute = attributes.get(key=f"{hashed_key}.{value}")
                            expected_value = expected_df.loc[
                                expected_df["column_name"] == original_key, value
                            ].values[0]
                            self.assertEqual(attribute.value, expected_value)

    def test_copy_attributes_with_no_previous_version(self):
        user = self.create_user(email="superuser@blsq.com", is_superuser=True)
        user2 = self.create_user(email="notsu@blsq.com")
        workspace = self.create_workspace(
            principal=user, name="workspace", description="desc"
        )
        self.join_workspace(user2, workspace, WorkspaceMembershipRole.EDITOR)
        dataset = self.create_dataset(
            principal=user, description="ds", name="Dataset", workspace=workspace
        )
        self.create_dataset_version(principal=user, dataset=dataset)
        self.client.force_login(user)
        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=user,
        )
        # No previous version
        previous_version = get_previous_version_file(file)
        self.assertIsNone(previous_version)

        # Copy attributes from previous version
        add_system_attributes(file, None)

        self.assertEqual(file.attributes.count(), 0)

    def test_copy_attributes_from_previous_version(self):
        user = self.create_user(email="superuser@blsq.com", is_superuser=True)
        user2 = self.create_user(email="notsu@blsq.com")
        workspace = self.create_workspace(
            principal=user, name="workspace", description="desc"
        )
        self.join_workspace(user2, workspace, WorkspaceMembershipRole.EDITOR)
        dataset = self.create_dataset(
            principal=user, description="ds", name="Dataset", workspace=workspace
        )
        self.create_dataset_version(principal=user, dataset=dataset)
        self.client.force_login(user)
        file = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=user,
        )

        metadataAttribute = MetadataAttribute.objects.create(
            key="key1",
            value="value1",
            system=False,
            object_content_type_id=ContentType.objects.get_for_model(
                DatasetVersionFile
            ).id,
            object_id=file.id,
        )
        # No previous version
        previous_version = get_previous_version_file(file)
        self.assertIsNone(previous_version)
        # Create previous version
        self.create_dataset_version(principal=user, dataset=dataset, name="v2")
        file2 = DatasetVersionFile.objects.create(
            dataset_version=dataset.latest_version,
            uri=dataset.latest_version.get_full_uri("file.csv"),
            created_by=user,
        )

        # Create new version with the same file
        previous_version_2 = get_previous_version_file(file2)
        self.assertEqual(previous_version_2.id, file.id)

        # Copy attributes from previous version
        add_system_attributes(file2, None)

        self.assertEqual(file2.attributes.all().count(), 1)
        self.assertEqual(file2.attributes.first().key, metadataAttribute.key)
        self.assertEqual(file2.attributes.first().value, metadataAttribute.value)
