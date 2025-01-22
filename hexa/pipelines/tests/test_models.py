from django.core import mail

from hexa.core.test import TestCase
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

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test pipeline",
            code="my-pipeline",
            description="This is a test pipeline",
        )
        cls.PIPELINE.upload_new_version(
            cls.USER_ADMIN, zipfile=b"", parameters=[], name="Version"
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
            {"param_1": 45, "param_2": 46},
            pipeline.last_version.config,
            "Config from previous version with a change of default values",
        )

    def test_get_or_create_template(self):
        template_name = "Test Template"
        template, _ = self.PIPELINE.get_or_create_template(
            name=template_name,
            code="test_code",
            description="Some description",
            config={"key": "value"},
        )
        self.assertIsNotNone(template)
        self.assertEqual(self.PIPELINE.template.name, template_name)
        self.PIPELINE.get_or_create_template(
            name="SOME RANDOM NAME",
            code="test_code",
            description="Some description",
            config={"key": "value"},
        )
        self.assertEqual(
            self.PIPELINE.template.name, template_name
        )  # Do not recreate a new template when it exists
