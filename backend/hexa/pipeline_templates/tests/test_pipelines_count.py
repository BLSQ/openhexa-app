"""Tests for pipelines_count annotation with tag filtering."""
from django.test import TestCase

from hexa.pipeline_templates.models import PipelineTemplate
from hexa.pipelines.models import Pipeline
from hexa.tags.models import Tag
from hexa.user_management.models import Organization, User
from hexa.workspaces.models import Workspace


class PipelinesCountTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organization.objects.create(name="Test Org")
        cls.user = User.objects.create(email="test@example.com")
        cls.workspace = Workspace.objects.create(
            name="Test Workspace", organization=cls.org
        )

        cls.source_pipeline = Pipeline.objects.create(
            workspace=cls.workspace,
            code="source_pipeline",
            name="Source Pipeline",
        )

        cls.template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_template",
            workspace=cls.workspace,
            source_pipeline=cls.source_pipeline,
        )

        cls.tag1 = Tag.objects.create(name="tag1")
        cls.tag2 = Tag.objects.create(name="tag2")
        cls.tag3 = Tag.objects.create(name="tag3")

        cls.template.tags.add(cls.tag1, cls.tag2, cls.tag3)

        for i in range(5):
            Pipeline.objects.create(
                workspace=cls.workspace,
                code=f"pipeline_{i}",
                name=f"Pipeline {i}",
                source_template=cls.template,
            )

    def test_pipelines_count_without_tag_filter(self):
        """Test that pipelines_count is correct without tag filtering."""
        template = (
            PipelineTemplate.objects.filter(id=self.template.id)
            .with_pipelines_count()
            .first()
        )

        self.assertEqual(template.pipelines_count, 5)

    def test_pipelines_count_with_tag_filter(self):
        """Test that pipelines_count is not inflated by tag filtering."""
        from django.db.models import Q

        template = (
            PipelineTemplate.objects.filter(id=self.template.id)
            .with_pipelines_count()
            .filter(Q(tags__name__icontains="tag"))
            .distinct()
            .first()
        )

        self.assertEqual(
            template.pipelines_count,
            5,
            "Count should be 5, not inflated by tag JOIN",
        )

    def test_pipelines_count_matches_graphql_query(self):
        """Test that pipelines_count matches the actual GraphQL query pattern."""
        from django.db.models import Q

        search = ""
        template = (
            PipelineTemplate.objects.filter(id=self.template.id)
            .select_related("workspace", "source_pipeline")
            .prefetch_related("tags")
            .with_pipelines_count()
            .filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(tags__name__icontains=search)
                | Q(functional_type__icontains=search)
            )
            .distinct()
            .first()
        )

        self.assertEqual(
            template.pipelines_count,
            5,
            "Count should be 5 even with full GraphQL query pattern",
        )

    def test_pipelines_count_with_multiple_tags_doesnt_multiply(self):
        """Test that having multiple tags doesn't multiply the count."""
        expected_count = self.template.pipelines.filter(deleted_at__isnull=True).count()

        template = (
            PipelineTemplate.objects.filter(id=self.template.id)
            .with_pipelines_count()
            .filter(tags__in=[self.tag1, self.tag2, self.tag3])
            .distinct()
            .first()
        )

        self.assertEqual(
            template.pipelines_count,
            expected_count,
            f"Count should be {expected_count}, not multiplied by number of tags",
        )
