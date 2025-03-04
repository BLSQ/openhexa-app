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
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
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
            self.USER_ADMIN, self.WORKSPACE2
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
