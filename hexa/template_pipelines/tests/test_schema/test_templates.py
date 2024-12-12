from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineVersion,
)
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
)


class TemplatesTest(GraphQLTestCase):
    USER_ROOT = None
    PIPELINE = None
    PIPELINE_VERSION = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WS1 = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS1",
                description="Workspace 1",
            )
        cls.PIPELINE = Pipeline.objects.create(name="Test Pipeline", workspace=cls.WS1)
        cls.PIPELINE_VERSION = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            version_number=1,
            description="Initial version",
        )

    def test_create_template_version(self):
        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
                mutation createTemplateVersion($input: CreateTemplateVersionInput!) {
                    createTemplateVersion(input: $input) {
                        success errors template {name code version {version_number}}
                    }
                }
            """,
            {
                "input": {
                    "name": "Template1",
                    "code": "template_code",
                    "description": "A test template",
                    "config": "{}",
                    "workspace_slug": self.WS1.slug,
                    "pipeline_id": str(self.PIPELINE.id),
                    "pipeline_version_id": str(self.PIPELINE_VERSION.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "template": {"name": "Template1", "code": "template_code"},
            },
            r["data"]["createTemplateVersion"],
        )
        r = self.run_query(
            """
                mutation createTemplateVersion($input: CreateTemplateVersionInput!) {
                    createTemplateVersion(input: $input) {
                        success errors template {name code version {version_number}}
                    }
                }
            """,
            {
                "input": {
                    "workspace_slug": self.WS1.slug,
                    "pipeline_id": self.PIPELINE.id,
                    "pipeline_version_id": self.PIPELINE_VERSION.id,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "template": {"name": "Template1", "code": "template_code"},
            },
            r["data"]["createTemplateVersion"],
        )
