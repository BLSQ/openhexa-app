from unittest.mock import patch

from django.core import mail

from hexa.core.test import TestCase
from hexa.pipeline_templates.models import PipelineTemplateVersion
from hexa.pipelines.models import (
    Pipeline,
    PipelineNotificationLevel,
    PipelineRecipient,
    PipelineRunLogLevel,
    PipelineRunState,
    PipelineRunTrigger,
)
from hexa.pipelines.utils import mail_run_recipients
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class TestPipelineRunLogLevel(TestCase):
    def test_parse_log_level(self):
        test_cases = [
            (0, PipelineRunLogLevel.DEBUG),
            (1, PipelineRunLogLevel.INFO),
            (2, PipelineRunLogLevel.WARNING),
            (3, PipelineRunLogLevel.ERROR),
            (4, PipelineRunLogLevel.CRITICAL),
            ("0", PipelineRunLogLevel.DEBUG),
            ("1", PipelineRunLogLevel.INFO),
            ("2", PipelineRunLogLevel.WARNING),
            ("3", PipelineRunLogLevel.ERROR),
            ("4", PipelineRunLogLevel.CRITICAL),
            ("DEBUG", PipelineRunLogLevel.DEBUG),
            ("INFO", PipelineRunLogLevel.INFO),
            ("WARNING", PipelineRunLogLevel.WARNING),
            ("ERROR", PipelineRunLogLevel.ERROR),
            ("CRITICAL", PipelineRunLogLevel.CRITICAL),
            ("invalid", PipelineRunLogLevel.INFO),
            (5, PipelineRunLogLevel.INFO),
            (-1, PipelineRunLogLevel.INFO),
        ]
        for value, expected in test_cases:
            with self.subTest(value=value):
                self.assertEqual(PipelineRunLogLevel.parse_log_level(value), expected)


class PipelineTest(TestCase):
    def create_recipient(
        self,
        user: User,
        pipeline: Pipeline,
        notification_level: PipelineNotificationLevel,
    ):
        return PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=user,
            notification_level=notification_level,
        )

    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com",
            "admin",
            analytics_enabled=True,
            is_superuser=True,
        )
        cls.USER_FOO = User.objects.create_user(
            "foo@bluesquarehub.com",
            "foopassword",
        )

        cls.USER_BAR = User.objects.create_user("bar@bluesquarehub.com", "barpassword")

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Sandbox",
            description="This is a sandbox workspace ",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE2 = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Sandbox2",
            description="This is a sandbox workspace ",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE2 = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Sandbox2",
            description="This is a sandbox workspace ",
            countries=[{"code": "AL"}],
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test pipeline",
            code="my-pipeline",
            description="This is a test pipeline",
        )
        cls.PIPELINE.upload_new_version(
            cls.USER_ADMIN,
            zipfile=b"",
            name="Version",
            parameters=[
                {"code": "param_1", "name": "Param 1", "default": 123, "type": "int"},
                {"code": "param_2", "name": "Param 2", "default": 456, "type": "int"},
            ],
            config={"param_1": 1234, "param_2": 4567},
        )

    def test_mail_run_recipients_mail_not_sent(self):
        self.client.force_login(self.USER_ADMIN)
        self.create_recipient(
            pipeline=self.PIPELINE,
            user=self.USER_BAR,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        run = self.PIPELINE.run(
            user=self.USER_ADMIN,
            pipeline_version=self.PIPELINE.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.SUCCESS
        run.save()

        mail_run_recipients(run)

        self.assertEqual(len(mail.outbox), 0)

    def test_mail_run_recipients_mail_success_only_recipients(self):
        self.client.force_login(self.USER_ADMIN)
        self.create_recipient(
            pipeline=self.PIPELINE,
            user=self.USER_BAR,
            notification_level=PipelineNotificationLevel.ERROR,
        )
        self.create_recipient(
            pipeline=self.PIPELINE,
            user=self.USER_FOO,
            notification_level=PipelineNotificationLevel.ERROR,
        )
        self.create_recipient(
            pipeline=self.PIPELINE,
            user=self.USER_ADMIN,
            notification_level=PipelineNotificationLevel.ALL,
        )

        run = self.PIPELINE.run(
            user=self.USER_ADMIN,
            pipeline_version=self.PIPELINE.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.SUCCESS
        run.save()

        mail_run_recipients(run)
        recipients = [email.recipients()[0] for email in mail.outbox]

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(
            all(
                [
                    self.USER_FOO.email not in recipients,
                    self.USER_BAR.email not in recipients,
                ]
            )
        )
        self.assertTrue(
            self.USER_ADMIN.email in recipients,
        )

    def test_mail_run_recipients_mail_all_recipients(self):
        self.client.force_login(self.USER_ADMIN)
        self.create_recipient(
            pipeline=self.PIPELINE,
            user=self.USER_BAR,
            notification_level=PipelineNotificationLevel.ERROR,
        )
        self.create_recipient(
            pipeline=self.PIPELINE,
            user=self.USER_FOO,
            notification_level=PipelineNotificationLevel.ERROR,
        )
        self.create_recipient(
            pipeline=self.PIPELINE,
            user=self.USER_ADMIN,
            notification_level=PipelineNotificationLevel.ALL,
        )

        run = self.PIPELINE.run(
            user=self.USER_ADMIN,
            pipeline_version=self.PIPELINE.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.FAILED
        run.save()

        mail_run_recipients(run)
        self.assertEqual(len(mail.outbox), 3)

    def test_get_config_from_previous_version(self):
        pipeline = Pipeline.objects.create(
            name="Test pipeline",
        )
        pipeline.upload_new_version(
            user=self.USER_ADMIN,
            zipfile=b"",
            parameters=[
                {
                    "choices": None,
                    "code": "param_1",
                    "default": None,
                    "help": None,
                    "multiple": False,
                    "name": "Param 1",
                    "required": True,
                    "type": "int",
                },
                {
                    "choices": None,
                    "code": "param_2",
                    "default": None,
                    "help": None,
                    "multiple": False,
                    "name": "Param 2",
                    "required": True,
                    "type": "int",
                },
            ],
            name="Version 1",
            config={"param_1": 43, "param_2": 42},
        )
        self.assertEqual(
            {"param_1": 43, "param_2": 42},
            pipeline.last_version.config,
            "Initial config",
        )
        pipeline.upload_new_version(
            user=self.USER_ADMIN,
            zipfile=b"",
            parameters=[
                {
                    "choices": None,
                    "code": "param_1",
                    "default": None,
                    "help": None,
                    "multiple": False,
                    "name": "Param 1",
                    "required": True,
                    "type": "int",
                },
                {
                    "choices": None,
                    "code": "param_3",
                    "default": None,
                    "help": None,
                    "multiple": False,
                    "name": "Param 3",
                    "required": True,
                    "type": "int",
                },
            ],
            name="Version 2",
            config=None,
        )
        self.assertEqual(
            {"param_1": 43},
            pipeline.last_version.config,
            "Config from previous version with a partial change of parameters",
        )
        pipeline.upload_new_version(
            user=self.USER_ADMIN,
            zipfile=b"",
            parameters=[
                {
                    "choices": None,
                    "code": "param_1",
                    "default": 45,
                    "help": None,
                    "multiple": False,
                    "name": "Param 1",
                    "required": True,
                    "type": "int",
                },
                {
                    "choices": None,
                    "code": "param_2",
                    "default": 46,
                    "help": None,
                    "multiple": False,
                    "name": "Param 2",
                    "required": True,
                    "type": "int",
                },
            ],
            name="Version 3",
            config=None,
        )
        self.assertEqual(
            {"param_1": 43, "param_2": 46},
            pipeline.last_version.config,
            "Config from previous version with a change of default values",
        )

    def test_get_or_create_template(self):
        template_name = "Test Template"
        template, _ = self.PIPELINE.get_or_create_template(
            name=template_name,
            code="test_code",
            description="Some description",
        )
        self.assertIsNotNone(template)
        self.assertEqual(self.PIPELINE.template.name, template_name)
        self.PIPELINE.get_or_create_template(
            name="SOME RANDOM NAME",
            code="test_code",
            description="Some description",
        )
        self.assertEqual(
            self.PIPELINE.template.name, template_name
        )  # Do not recreate a new template when it exists

        template.delete()

        self.PIPELINE.get_or_create_template(
            name="New name", code="New code", description="New description"
        )
        self.assertFalse(template.is_deleted)
        self.assertEqual(template.name, "New name")
        self.assertEqual(template.code, "New code")
        self.assertEqual(template.description, "New description")

    def test_new_template_version(self):
        template, _ = self.PIPELINE.get_or_create_template(
            name="Test Template",
            code="test_code",
            description="Some description",
        )
        template_version = template.create_version(
            self.PIPELINE.last_version, changelog="First version"
        )

        created_pipeline_version = template_version.create_pipeline_version(
            self.WORKSPACE2, principal=self.USER_ADMIN
        )
        created_pipeline = created_pipeline_version.pipeline
        self.assertFalse(created_pipeline.has_new_template_versions)

        for i in range(2, 5):
            self.PIPELINE.upload_new_version(
                user=self.USER_ADMIN,
                zipfile=b"",
                parameters=[
                    {
                        "code": "param_1",
                        "name": "Param 1",
                        "default": 444,
                        "type": "int",
                    },
                    {
                        "code": "param_3",
                        "name": "Param 3",
                        "default": 666,
                        "type": "int",
                    },
                    {"code": "param_4", "name": "Param 4", "type": "dhis2"},
                ],
                name=f"Version {i}",
                config={"param_1": 888, "param_3": 999, "param_4": "dhis2"},
            )
            template.create_version(
                self.PIPELINE.last_version, changelog=f"Changelog {i}"
            )

        self.assertEqual(
            PipelineTemplateVersion.objects.get_updates_for(created_pipeline).count(), 3
        )

        created_pipeline.upload_new_version(
            self.USER_ADMIN,
            zipfile=b"",
            name="Version",
            parameters=[
                {"code": "param_1", "name": "Param 1", "default": 123, "type": "int"},
                {"code": "param_5", "name": "Param 5", "default": 456, "type": "int"},
            ],
            config={"param_1": 1234, "param_5": 4567},
        )

        self.assertEqual(
            PipelineTemplateVersion.objects.get_updates_for(created_pipeline).count(), 3
        )

        template.upgrade_pipeline(self.USER_ADMIN, created_pipeline)

        self.assertFalse(created_pipeline.has_new_template_versions)
        self.assertEqual(
            created_pipeline.last_version.config, {"param_1": 1234, "param_3": 666}
        )

    def test_create_if_has_perm(self):
        workspace = Workspace.objects.create(
            name="Test Workspace",
            description="A workspace for testing",
        )

        with patch("secrets.token_hex", return_value="abc123"):
            pipeline1 = Pipeline.objects.create_if_has_perm(
                name="Test Pipeline",
                principal=self.USER_ADMIN,
                workspace=workspace,
            )
            pipeline2 = Pipeline.objects.create_if_has_perm(
                name="Test Pipeline",
                principal=self.USER_ADMIN,
                workspace=workspace,
            )

        self.assertNotEqual(pipeline1.code, pipeline2.code)
        self.assertEqual(pipeline1.code, "test-pipeline")
        self.assertEqual(pipeline2.code, "test-pipeline-abc123")


class PipelineOrganizationAdminOwnerPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-pipeline",
            organization_type="CORPORATE",
        )

        cls.ORG_OWNER_USER = User.objects.create_user(
            "owner@bluesquarehub.com", "password"
        )
        cls.ORG_ADMIN_USER = User.objects.create_user(
            "admin@bluesquarehub.com", "password"
        )
        cls.ORG_MEMBER_USER = User.objects.create_user(
            "member@bluesquarehub.com", "password"
        )
        cls.NON_ORG_USER = User.objects.create_user(
            "nonorg@bluesquarehub.com", "password"
        )

        cls.WORKSPACE_ADMIN = User.objects.create_user(
            "workspace_admin@bluesquarehub.com", "password", is_superuser=True
        )

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_OWNER_USER,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_ADMIN_USER,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_MEMBER_USER,
            role=OrganizationMembershipRole.MEMBER,
        )

        cls.WORKSPACE_1 = Workspace.objects.create_if_has_perm(
            cls.WORKSPACE_ADMIN,
            name="Workspace 1",
            description="First workspace in organization",
            organization=cls.ORGANIZATION,
        )

        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.WORKSPACE_ADMIN,
            name="Workspace 2",
            description="Second workspace in organization",
            organization=cls.ORGANIZATION,
        )

        cls.WORKSPACE_ADMIN.is_superuser = False
        cls.WORKSPACE_ADMIN.save()

        cls.PIPELINE_1 = Pipeline.objects.create(
            workspace=cls.WORKSPACE_1,
            name="Pipeline in workspace 1",
            code="pipeline-1",
            description="Pipeline in workspace where org admin/owner is not a member",
        )

        cls.PIPELINE_2 = Pipeline.objects.create(
            workspace=cls.WORKSPACE_2,
            name="Pipeline in workspace 2",
            code="pipeline-2",
            description="Pipeline in another workspace in same org",
        )

    def test_organization_owner_can_access_all_pipelines_in_organization(self):
        pipelines = Pipeline.objects.filter_for_user(self.ORG_OWNER_USER)

        self.assertIn(self.PIPELINE_1, pipelines)
        self.assertIn(self.PIPELINE_2, pipelines)

    def test_organization_admin_can_access_all_pipelines_in_organization(self):
        pipelines = Pipeline.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.PIPELINE_1, pipelines)
        self.assertIn(self.PIPELINE_2, pipelines)

    def test_organization_member_cannot_access_pipelines_from_non_member_workspaces(
        self,
    ):
        pipelines = Pipeline.objects.filter_for_user(self.ORG_MEMBER_USER)

        self.assertNotIn(self.PIPELINE_1, pipelines)
        self.assertNotIn(self.PIPELINE_2, pipelines)

    def test_non_organization_member_cannot_access_organization_pipelines(self):
        pipelines = Pipeline.objects.filter_for_user(self.NON_ORG_USER)

        self.assertNotIn(self.PIPELINE_1, pipelines)
        self.assertNotIn(self.PIPELINE_2, pipelines)

    def test_organization_admin_owner_access_combined_with_workspace_membership(self):
        WorkspaceMembership.objects.create(
            workspace=self.WORKSPACE_1,
            user=self.ORG_ADMIN_USER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        pipelines = Pipeline.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.PIPELINE_1, pipelines)
        self.assertIn(self.PIPELINE_2, pipelines)

    def test_superuser_still_has_access_to_all_pipelines(self):
        superuser = User.objects.create_user(
            "superuser@bluesquarehub.com", "password", is_superuser=True
        )

        pipelines = Pipeline.objects.filter_for_user(superuser)

        self.assertIn(self.PIPELINE_1, pipelines)
        self.assertIn(self.PIPELINE_2, pipelines)

    def test_pipeline_filter_for_workspace_slugs_with_org_admin_owner(self):
        workspace_slugs = [self.WORKSPACE_1.slug, self.WORKSPACE_2.slug]

        owner_pipelines = Pipeline.objects.filter_for_workspace_slugs(
            self.ORG_OWNER_USER, workspace_slugs
        )
        admin_pipelines = Pipeline.objects.filter_for_workspace_slugs(
            self.ORG_ADMIN_USER, workspace_slugs
        )
        member_pipelines = Pipeline.objects.filter_for_workspace_slugs(
            self.ORG_MEMBER_USER, workspace_slugs
        )

        self.assertIn(self.PIPELINE_1, owner_pipelines)
        self.assertIn(self.PIPELINE_2, owner_pipelines)
        self.assertIn(self.PIPELINE_1, admin_pipelines)
        self.assertIn(self.PIPELINE_2, admin_pipelines)
        self.assertNotIn(self.PIPELINE_1, member_pipelines)
        self.assertNotIn(self.PIPELINE_2, member_pipelines)
