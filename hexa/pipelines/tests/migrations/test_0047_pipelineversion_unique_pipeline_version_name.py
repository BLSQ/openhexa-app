from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase


class Migrator:
    def __init__(self, connection=connection):
        self.executor = MigrationExecutor(connection)
        self.apps = None

    def migrate(self, app_label: str, migration: str):
        target = [(app_label, migration)]
        self.executor.loader.build_graph()
        self.executor.migrate(target)
        self.apps = self.executor.loader.project_state(target).apps


class MigrationTest(TestCase):  # TODO : rename
    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(
            "pipelines", "0046_pipelinerecipient_notification_level_and_more"
        )

    def test_populate_usernames(self):  # TODO : rename
        pipeline_code = "simple-etl"
        Pipeline = self.migrator.apps.get_model("pipelines", "Pipeline")
        PipelineVersion = self.migrator.apps.get_model("pipelines", "PipelineVersion")
        pipeline = Pipeline.objects.create(code=pipeline_code)
        PipelineVersion.objects.create(
            pipeline=pipeline, name="version1", created_at="2023-01-01"
        )
        PipelineVersion.objects.create(
            pipeline=pipeline, name="version1", created_at="2023-01-02"
        )
        PipelineVersion.objects.create(
            pipeline=pipeline, name="version1", created_at="2023-01-03"
        )

        self.migrator.migrate(
            "pipelines", "0047_pipelineversion_unique_pipeline_version_name"
        )

        Pipeline = self.migrator.apps.get_model("pipelines", "Pipeline")
        PipelineVersion = self.migrator.apps.get_model("pipelines", "PipelineVersion")
        pipeline = Pipeline.objects.get(code=pipeline_code)
        versions = PipelineVersion.objects.filter(pipeline=pipeline).order_by(
            "created_at"
        )

        self.assertEqual(versions[0].name, "version1 (v1)")
        self.assertEqual(versions[1].name, "version1 (v2)")
        self.assertEqual(versions[2].name, "version1")
