from django.test import TestCase

from hexa.core.test.migrator import Migrator


class Migration0049Test(TestCase):
    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate("pipelines", "0049_pipelineversion_version_number")
        self.pipeline_code = "simple-etl"

    def get_pipeline_model(self):
        return self.migrator.apps.get_model("pipelines", "Pipeline")

    def get_pipeline_version_model(self):
        return self.migrator.apps.get_model("pipelines", "PipelineVersion")

    def test_set_version_numbers(self):
        PipelineVersion = self.get_pipeline_version_model()
        pipeline = self.get_pipeline_model().objects.create(code=self.pipeline_code)
        for version_number, name, date in [
            (3, "3", "2023-01-01"),
            (10, "10", "2023-01-02"),
            (20, "20", "2023-01-03"),
        ]:
            PipelineVersion.objects.create(
                pipeline=pipeline,
                version_number=version_number,
                name=name,
                created_at=date,
            )

        self.migrator.migrate("pipelines", "0050_pipelineversion_set_version_numbers")

        pipeline = self.get_pipeline_model().objects.get(code=self.pipeline_code)
        versions = (
            self.get_pipeline_version_model()
            .objects.filter(pipeline=pipeline)
            .order_by("created_at")
        )
        for i, version in enumerate(versions):
            self.assertEqual(version.version_number, i + 1)
