from django.core import mail

from hexa.core.test import TestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineNotificationLevel,
    PipelineRecipient,
    PipelineRunState,
    PipelineRunTrigger,
)
from hexa.pipelines.utils import mail_run_recipients
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
)


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
