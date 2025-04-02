from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import User
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

    def create_version(self, version, user=None):
        user = user or self.USER_ADMIN
        self.client.force_login(user)
        return self.run_query(
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

    def test_create_version(self, version="First Version", user=None):
        r = self.create_version(version, user)
        self.assertEqual(r["data"]["uploadPipeline"]["success"], True)

    def test_duplicate_versions(self):
        name = "Version 1"
        self.create_version(name)
        r = self.create_version(name)
        self.assertEqual(r["data"]["uploadPipeline"]["success"], False)
        self.assertEqual(
            r["data"]["uploadPipeline"]["errors"], ["DUPLICATE_PIPELINE_VERSION_NAME"]
        )

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
                    "config": {"dhis2_connection": "abcd"},
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
                    "config": {"dhis2_connection": "abcd"},
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

    def test_increment_version_number_on_save(self):
        self.test_create_version("First version")
        self.test_create_version("Second version")
        self.create_version(None)

        pipeline = Pipeline.objects.filter(code=self.PIPELINE.code).first()

        first_version = pipeline.versions.filter(name="First version").first()
        self.assertEqual(first_version.version_number, 1)
        self.assertEqual(first_version.version_name, "First version [v1]")
        self.assertEqual(first_version.display_name, "My Pipeline - First version [v1]")

        self.assertEqual(
            pipeline.versions.filter(name="Second version").first().version_number, 2
        )

        third_version = pipeline.versions.filter(name__isnull=True).first()
        self.assertEqual(third_version.version_number, 3)
        self.assertEqual(third_version.version_name, "v3")
        self.assertEqual(third_version.display_name, "My Pipeline - v3")
