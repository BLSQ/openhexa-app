from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
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

    def test_create_version(self, version="First Version", user=None):
        if user is None:
            user = self.USER_ADMIN
        self.client.force_login(user)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "name": version,
                    "parameters": [],
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(r["data"]["uploadPipeline"]["success"], True)

    def test_version_is_latest(self):
        self.test_create_version("Version 1")
        self.test_create_version("Version 2")
        self.test_create_version("Version 3")

        self.assertTrue(self.PIPELINE.last_version.is_latest_version)
        self.assertFalse(self.PIPELINE.versions.last().is_latest_version)

    def test_update_version(self):
        self.test_create_version("Version 1")

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description
                        config
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {},
                }
            },
        )

        self.assertEqual(
            r["data"]["updatePipelineVersion"],
            {
                "success": True,
                "errors": [],
                "pipelineVersion": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {},
                },
            },
        )

    def test_create_version_with_unschedulable_config(self):
        self.test_create_version_with_parameters(version="Version 2 with parameters")

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description
                        config
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"param_example": "example_value"},
                }
            },
        )
        self.assertEqual(
            r["data"]["updatePipelineVersion"],
            {
                "success": True,
                "errors": [],
                "pipelineVersion": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"param_example": "example_value"},
                },
            },
        )

        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description
                        config
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                    "config": {"param_example": None},
                }
            },
        )
        self.assertEqual(
            "Cannot push an unschedulable new version for a scheduled pipeline.",
            r["errors"][0]["message"],
        )

    def test_create_version_not_admin(self):
        self.client.force_login(self.USER_SABRINA)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "name": "version",
                    "parameters": [],
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            r["data"]["uploadPipeline"],
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
        )

    def test_update_version_not_admin(self):
        self.test_create_version("Version 1", user=self.USER_ADMIN)

        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation updatePipelineVersion($input: UpdatePipelineVersionInput!) {
                updatePipelineVersion(input: $input) {
                    success
                    errors
                    pipelineVersion {
                        id
                        name
                        externalLink
                        description

                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(self.PIPELINE.last_version.id),
                    "name": "New Version Name",
                    "externalLink": "https://example.com",
                    "description": "New Description",
                }
            },
        )

        self.assertEqual(
            r["data"]["updatePipelineVersion"],
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
                "pipelineVersion": None,
            },
        )

    def test_create_version_with_parameters(self, version="Filler", user=None):
        if user is None:
            user = self.USER_ADMIN
        self.client.force_login(user)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "code": self.PIPELINE.code,
                    "workspaceSlug": self.WORKSPACE.slug,
                    "name": version,
                    "parameters": [
                        {
                            "code": "param_example",
                            "name": "Param Example",
                            "type": "str",
                            "help": "Param Example's Help",
                            "default": None,
                            "multiple": False,
                            "required": True,
                            "choices": [],
                        }
                    ],
                    "zipfile": "",
                }
            },
        )
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).first()
        pipeline.schedule = "0 15 * * *"
        pipeline.save()
        self.assertEqual(r["data"]["uploadPipeline"]["success"], True)
