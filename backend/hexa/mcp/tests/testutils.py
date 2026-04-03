import io
import zipfile
from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.utils import timezone

from hexa.core.test import TestCase
from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile
from hexa.files import storage
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVersion,
)
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


# MCP tools execute GraphQL queries internally rather than through HTTP,
# so we need a base test case with pre-built fixtures (workspace, pipeline,
# dataset, etc.) that the tools can query against.
class MCPTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        storage.reset()
        storage.create_bucket(settings.WORKSPACE_DATASETS_BUCKET)

        cls.USER_ADMIN = User.objects.create_user(
            "admin@openhexa.org", "password", is_superuser=True
        )
        cls.USER_VIEWER = User.objects.create_user("viewer@openhexa.org", "password")
        cls.USER_OUTSIDER = User.objects.create_user(
            "outsider@openhexa.org", "password"
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN,
                name="Test Workspace",
                description="A test workspace",
            )

        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Pipeline",
            code="test-pipeline",
            description="A test pipeline",
        )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("pipeline.py", 'print("hello")')
        cls.ZIP_CONTENT = zip_buffer.getvalue()

        cls.PIPELINE_VERSION = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            user=cls.USER_ADMIN,
            zipfile=cls.ZIP_CONTENT,
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "str",
                    "required": True,
                    "default": "default",
                    "multiple": False,
                    "help": "A test parameter",
                    "choices": [],
                }
            ],
        )

        cls.PIPELINE_RUN = PipelineRun.objects.create(
            pipeline=cls.PIPELINE,
            pipeline_version=cls.PIPELINE_VERSION,
            user=cls.USER_ADMIN,
            run_id="test-run-1",
            execution_date=timezone.now(),
            trigger_mode=PipelineRunTrigger.MANUAL,
            state=PipelineRunState.SUCCESS,
            duration=timedelta(seconds=42),
            config={"param1": "value1"},
        )

        cls.DATASET = Dataset.objects.create_if_has_perm(
            cls.USER_ADMIN,
            workspace=cls.WORKSPACE,
            name="Test Dataset",
            description="A test dataset",
        )

        cls.DATASET_VERSION = DatasetVersion.objects.create_if_has_perm(
            cls.USER_ADMIN,
            dataset=cls.DATASET,
            name="v1",
            changelog="Initial version",
        )

        cls.DATASET_FILE = DatasetVersionFile.objects.create_if_has_perm(
            cls.USER_ADMIN,
            dataset_version=cls.DATASET_VERSION,
            uri="test-file.csv",
            content_type="text/csv",
        )

        cls.TEMPLATE_SOURCE_PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Template Source",
            code="template-source",
        )
        cls.TEMPLATE_SOURCE_VERSION = PipelineVersion.objects.create(
            pipeline=cls.TEMPLATE_SOURCE_PIPELINE,
            user=cls.USER_ADMIN,
            zipfile=cls.ZIP_CONTENT,
            parameters=[],
        )
        cls.TEMPLATE = PipelineTemplate.objects.create(
            name="Test Template",
            code="test-template",
            description="A test template",
            workspace=cls.WORKSPACE,
            source_pipeline=cls.TEMPLATE_SOURCE_PIPELINE,
        )
        cls.TEMPLATE_VERSION = PipelineTemplateVersion.objects.create(
            template=cls.TEMPLATE,
            version_number=1,
            user=cls.USER_ADMIN,
            source_pipeline_version=cls.TEMPLATE_SOURCE_VERSION,
        )

        cls.CONNECTION = Connection.objects.create_if_has_perm(
            cls.USER_ADMIN,
            workspace=cls.WORKSPACE,
            name="Test Connection",
            slug="test-connection",
            connection_type=ConnectionType.CUSTOM,
        )
