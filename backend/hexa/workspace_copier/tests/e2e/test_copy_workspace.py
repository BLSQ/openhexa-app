"""End-to-end scenario tests for a full workspace copy.

Each test is one real ``run_copy`` invocation; assertions go against the ORM on
the target side plus the returned ``CopyResult``.
"""

from hexa.workspace_copier.results import format_summary
from hexa.workspaces.models import Connection, Workspace

from .harness import WorkspaceCopierE2ETestCase


class FreshCopyTest(WorkspaceCopierE2ETestCase):
    def test_fresh_full_copy(self):
        source = self.create_source_workspace(
            name="Malaria Analysis",
            description="Everything about malaria",
            docker_image="blsq/openhexa-base:2.0",
        )
        self.add_files(
            source,
            {
                "data/a.csv": b"a,b,c\n1,2,3\n",
                "notebooks/nb.ipynb": b'{"cells": []}',
                ".ipynb_checkpoints/scratch.ipynb": b"should not be copied",
            },
        )
        self.add_connection(source)
        self.add_pipeline(source)

        source_token = self.create_source_account(source)
        target_token = self.create_target_account(self.target_org)

        result = self.run_copy(
            source_slug=source.slug,
            source_token=source_token,
            target_token=target_token,
            target_organization_id=str(self.target_org.id),
        )

        target = Workspace.objects.get(slug=result.workspace_slug)
        self.assertEqual(target.organization_id, self.target_org.id)
        self.assertEqual(target.name, "Malaria Analysis")
        self.assertEqual(target.description, "Everything about malaria")
        self.assertEqual(
            sorted(str(c) for c in target.countries),
            sorted(str(c) for c in source.countries),
        )
        self.assertEqual(target.docker_image, "blsq/openhexa-base:2.0")
        self.assertNotEqual(target.slug, source.slug)

        # Files: the two real files copied with identical bytes; the
        # .ipynb_checkpoints file skipped.
        copied_keys = {path for path, _ in result.files.copied}
        self.assertEqual(copied_keys, {"data/a.csv", "notebooks/nb.ipynb"})
        self.assertEqual(result.files.skipped, 0)
        self.assertEqual(result.files.failed, [])
        from hexa.files import storage

        self.assertEqual(
            storage.read_object(target.bucket_name, "data/a.csv"),
            b"a,b,c\n1,2,3\n",
        )

        # Connections recreated including the secret value.
        target_conn = Connection.objects.get(workspace=target, slug="my-postgres")
        password_field = target_conn.fields.get(code="password")
        self.assertTrue(password_field.secret)
        self.assertEqual(password_field.value, "s3cr3t")

        # Pipeline recreated with its versions, and the scheduled version bound
        # to the target's re-numbered newest version.
        self.assertEqual(len(result.pipelines.created), 1)
        target_pipeline = target.pipeline_set.get(code="my-pipeline")
        self.assertEqual(target_pipeline.schedule, "0 6 * * *")
        self.assertEqual(target_pipeline.versions.count(), 2)
        self.assertIsNotNone(target_pipeline.scheduled_pipeline_version)
        self.assertEqual(
            target_pipeline.scheduled_pipeline_version,
            target_pipeline.versions.order_by("-version_number").first(),
        )

        # Database copier: skipped with a warning (remote→remote).
        self.assertTrue(
            any("Database not copied" in w for w in result.warnings),
            result.warnings,
        )

        summary = format_summary(result)
        self.assertIn("Malaria Analysis", summary)
