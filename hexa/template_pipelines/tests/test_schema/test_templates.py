from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineType,
)
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class TemplatesTest(GraphQLTestCase):
    USER_ROOT = None
    USER_NOOB = None
    WS1 = None
    WS2 = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.USER_NOOB = User.objects.create_user(
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
            feature=Feature.objects.create(code="pipeline_webhook"), user=cls.USER_ROOT
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_NOOB
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_SABRINA
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WS1 = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS1",
                description="Workspace 1",
            )
            cls.WS2 = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS2",
                description="Workspace 2",
            )
        cls.WORKSPACE2_MEMBERSHIP_1 = WorkspaceMembership.objects.create(
            workspace=cls.WS2,
            user=cls.USER_NOOB,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.WORKSPACE1_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            workspace=cls.WS1,
            user=cls.USER_LAMBDA,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.WORKSPACE1_MEMBERSHIP_3 = WorkspaceMembership.objects.create(
            workspace=cls.WS1,
            user=cls.USER_SABRINA,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_create_pipeline(self):
        self.assertEqual(0, len(Pipeline.objects.all()))

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
                mutation createPipeline($input: CreatePipelineInput!) {
                    createPipeline(input: $input) {
                        success errors pipeline {name code}
                    }
                }
            """,
            {
                "input": {
                    "code": "new_pipeline",
                    "name": "MonBeauPipeline",
                    "workspaceSlug": self.WS1.slug,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {"name": "MonBeauPipeline", "code": "new_pipeline"},
            },
            r["data"]["createPipeline"],
        )
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).get()

        self.assertEqual(1, len(Pipeline.objects.all()))
        self.assertEqual(1, len(Pipeline.objects.filter_for_user(self.USER_ROOT)))
        self.assertEqual(pipeline.type, PipelineType.ZIPFILE)

        return pipeline
