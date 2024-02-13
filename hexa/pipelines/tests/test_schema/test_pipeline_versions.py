from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class PipelineVersionsTest(GraphQLTestCase):
    USER_ROOT = None
    USER_ADMIN = None
    WORKSPACE = None
    PIPELINE = None

    @classmethod
    @mock_gcp_storage
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.USER_ADMIN = User.objects.create_user(
            "noob@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_LAMBDA = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_ADMIN
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_LAMBDA
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_SABRINA
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WORKSPACE = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS1",
                description="Workspace 1",
            )
        cls.WORKSPACE_MEMBERSHIP_1 = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_ADMIN,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WORKSPACE_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_SABRINA,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.PIPELINE = Pipeline.objects.create(
            code="pipeline", name="My Pipeline", workspace=cls.WORKSPACE
        )

    def test_create_version(self, user=None):
        if user is None:
            user = self.USER_ADMIN
        self.client.force_login(user)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    version
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "parameters": [],
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(r["data"]["uploadPipeline"]["success"], True)

    def test_version_is_latest(self):
        self.test_create_version()
        self.test_create_version()
        self.test_create_version()

        self.assertTrue(self.PIPELINE.last_version.is_latest_version)
        self.assertFalse(self.PIPELINE.versions.last().is_latest_version)
