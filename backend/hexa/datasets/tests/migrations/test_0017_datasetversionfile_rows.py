import pandas as pd
from unittest.mock import patch
from django.test import TestCase

from hexa.core.test.migrator import Migrator


class Migration0017DatasetVersionFileRowsTest(TestCase):
    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate("datasets", "0016_add_shared_with_organization")

    def get_version_file_model(self):
        return self.migrator.apps.get_model("datasets", "DatasetVersionFile")

    def get_sample_model(self):
        return self.migrator.apps.get_model("datasets", "DatasetFileSample")

    @patch("hexa.datasets.migrations.0017_datasetversionfile_rows.load_df")
    def test_rows_and_sample_are_filled(self, mock_load_df):
        """
        Ensures:
        - rows is correctly populated
        - sample is populated
        - only rows=None objects are processed
        """

        # Mock dataframe
        df = pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
            }
        )
        mock_load_df.return_value = df

        DatasetVersionFile = self.get_version_file_model()
        DatasetFileSample = self.get_sample_model()

        # Create object with rows=None (should be processed)
        version_file = DatasetVersionFile.objects.create(
            rows=None,
        )

        sample = DatasetFileSample.objects.create(
            dataset_version_file=version_file,
            sample=None,
        )

        # Create object with rows already set (should NOT be processed)
        untouched_file = DatasetVersionFile.objects.create(
            rows=999,
        )

        # Apply migration
        self.migrator.migrate(
            "datasets",
            "0017_datasetversionfile_rows",
        )

        # Reload models after migration
        DatasetVersionFile = self.get_version_file_model()
        DatasetFileSample = self.get_sample_model()

        version_file = DatasetVersionFile.objects.get(pk=version_file.pk)
        sample = DatasetFileSample.objects.get(pk=sample.pk)
        untouched_file = DatasetVersionFile.objects.get(pk=untouched_file.pk)

        # ----------- Assertions -----------
        # rows correctly filled
        self.assertEqual(3, version_file.rows)

        # sample correctly filled
        self.assertEqual(
            df.head(n=50).to_dict(orient="records"),
            sample.sample,
        )

        # untouched object remains unchanged
        self.assertEqual(999, untouched_file.rows)
