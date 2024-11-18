from django.test import TestCase

from hexa.core.test.migrator import Migrator


class Migration0047Test(TestCase):
    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(
            "pipelines", "0046_pipelinerecipient_notification_level_and_more"
        )
        self.pipeline_code = "simple-etl"

    def get_pipeline_model(self):
        return self.migrator.apps.get_model("pipelines", "Pipeline")

    def get_pipeline_version_model(self):
        return self.migrator.apps.get_model("pipelines", "PipelineVersion")

    def test_unique_pipelineversion_names(self):
        PipelineVersion = self.get_pipeline_version_model()
        pipeline = self.get_pipeline_model().objects.create(code=self.pipeline_code)
        for date in ["2023-01-01", "2023-01-02", "2023-01-03"]:
            PipelineVersion.objects.create(
                pipeline=pipeline, name="version1", created_at=date
            )

        self.migrator.migrate(
            "pipelines", "0047_pipelineversion_rename_duplicate_pipeline_version_name"
        )

        pipeline = self.get_pipeline_model().objects.get(code=self.pipeline_code)
        versions = (
            self.get_pipeline_version_model()
            .objects.filter(pipeline=pipeline)
            .order_by("created_at")
        )

        self.assertEqual(versions[0].name, "version1 (v1)")
        self.assertEqual(versions[1].name, "version1 (v2)")
        self.assertEqual(versions[2].name, "version1")
