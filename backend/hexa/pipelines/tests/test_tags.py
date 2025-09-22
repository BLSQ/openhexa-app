from unittest.mock import patch

from django.test import TestCase

from hexa.pipelines.models import Pipeline
from hexa.tags.models import InvalidTag, Tag
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class PipelineTagsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com", password="password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user,
                name="Test Workspace",
                description="A test workspace",
            )
        cls.pipeline = Pipeline.objects.create_if_has_perm(
            principal=cls.user, workspace=cls.workspace, name="Test Pipeline"
        )

    def test_add_tags_to_pipeline(self):
        tag1 = Tag.objects.create(name="ml")
        tag2 = Tag.objects.create(name="data-processing")

        self.pipeline.tags.add(tag1, tag2)
        self.pipeline.save()

        pipeline_tags = self.pipeline.tags.all()
        self.assertEqual(pipeline_tags.count(), 2)
        self.assertIn(tag1, pipeline_tags)
        self.assertIn(tag2, pipeline_tags)

    def test_filter_by_tags(self):
        """Test filtering pipelines by tags."""
        tag1 = Tag.objects.create(name="ml")
        tag2 = Tag.objects.create(name="data-processing")
        tag3 = Tag.objects.create(name="analytics")

        pipeline2 = Pipeline.objects.create_if_has_perm(
            principal=self.user, workspace=self.workspace, name="Pipeline 2"
        )

        self.pipeline.tags.add(tag1, tag2)
        self.pipeline.save()

        pipelines_with_ml = Pipeline.objects.filter_by_tags([tag1.name])
        self.assertIn(self.pipeline, pipelines_with_ml)
        self.assertNotIn(pipeline2, pipelines_with_ml)

        pipelines_with_tags = Pipeline.objects.filter_by_tags([tag1.name, tag2.name])
        self.assertIn(self.pipeline, pipelines_with_tags)
        self.assertNotIn(pipeline2, pipelines_with_tags)

        pipelines_with_analytics = Pipeline.objects.filter_by_tags([tag3.name])
        self.assertNotIn(self.pipeline, pipelines_with_analytics)
        self.assertNotIn(pipeline2, pipelines_with_analytics)

        no_pipelines = Pipeline.objects.filter_by_tags([])
        self.assertNotIn(self.pipeline, no_pipelines)
        self.assertNotIn(pipeline2, no_pipelines)

    def test_update_pipeline_tags(self):
        tag1 = Tag.objects.create(name="ml")
        tag2 = Tag.objects.create(name="data-processing")
        tag3 = Tag.objects.create(name="analytics")

        self.pipeline.tags.add(tag1, tag2)
        self.pipeline.save()

        self.pipeline.update_if_has_perm(self.user, tags=[tag2, tag3])

        updated_tags = list(self.pipeline.tags.all())
        self.assertEqual(len(updated_tags), 2)
        self.assertNotIn(tag1, updated_tags)
        self.assertIn(tag2, updated_tags)
        self.assertIn(tag3, updated_tags)

    def test_update_pipeline_with_empty_tags(self):
        tag1 = Tag.objects.create(name="ml")
        self.pipeline.tags.add(tag1)
        self.pipeline.save()

        self.pipeline.update_if_has_perm(self.user, tags=[])

        self.assertEqual(self.pipeline.tags.count(), 0)

    def test_tag_from_names_validation(self):
        tag1 = Tag.objects.create(name="ml")
        tag2 = Tag.objects.create(name="data-processing")

        tags = Tag.from_names(["ml", "data-processing"])
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

        with self.assertRaises(InvalidTag):
            Tag.from_names(["nonexistent"])

        with self.assertRaises(InvalidTag):
            Tag.from_names(["ml", "nonexistent"])

        empty_tags = Tag.from_names([])
        self.assertEqual(empty_tags.count(), 0)
