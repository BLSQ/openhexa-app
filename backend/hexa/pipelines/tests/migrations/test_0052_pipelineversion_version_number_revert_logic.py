from django.test import TestCase

from hexa.core.test.migrator import Migrator


class ReverseMigration0052Test(TestCase):
    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(
            "pipelines", "0052_pipelineversion_version_number_revert_logic"
        )
        self.pipeline_code = "simple-etl"

    def get_pipeline_model(self):
        return self.migrator.apps.get_model("pipelines", "Pipeline")

    def get_pipeline_version_model(self):
        return self.migrator.apps.get_model("pipelines", "PipelineVersion")

    def test_filling_empty_names(self):
        pipeline = self.get_pipeline_model().objects.create(code=self.pipeline_code)
        self.get_pipeline_version_model().objects.create(
            pipeline=pipeline,
            version_number=123,
            name=None,
            created_at="2023-01-01",
        )

        # Revert the migration
        self.migrator.migrate(
            "pipelines", "0051_pipelineversion_version_number_cleanup"
        )

        pipeline = self.get_pipeline_model().objects.get(code=self.pipeline_code)
        version = self.get_pipeline_version_model().objects.get(pipeline=pipeline)

        self.assertEqual("v123 (auto-generated name)", version.name)
