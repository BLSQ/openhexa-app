from decimal import Decimal
from unittest.mock import patch

from asgiref.sync import async_to_sync
from pydantic_ai import RunUsage
from pydantic_ai.models.test import TestModel

from hexa.assistant.ai_models import BuiltModel
from hexa.assistant.models import AiUsage
from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace


class AiUsageRecordTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("cost@example.com", "password")
        cls.workspace = create_workspace(name="Cost WS")

    def record(self, built_model, usage, **links):
        return async_to_sync(AiUsage.arecord)(
            built_model,
            usage,
            source=AiUsage.Source.NOTEBOOK,
            cost=Decimal("0.5"),
            organization_id=self.workspace.organization_id,
            workspace_id=self.workspace.id,
            user_id=self.user.id,
            **links,
        )

    def test_records_the_run(self):
        built = BuiltModel(TestModel(), "claude-opus-4-6", "google-vertex")
        row = self.record(
            built,
            RunUsage(input_tokens=10, cache_read_tokens=4, output_tokens=3),
            external_id="chatcmpl-1",
        )
        self.assertEqual(AiUsage.objects.get(), row)
        self.assertEqual(
            (row.provider, row.model_name, row.cost, row.external_id),
            ("google-vertex", "claude-opus-4-6", Decimal("0.5"), "chatcmpl-1"),
        )
        self.assertEqual(
            (row.input_tokens, row.cache_read_tokens, row.output_tokens), (10, 4, 3)
        )
        self.assertEqual(
            (row.organization, row.workspace, row.user),
            (
                self.workspace.organization,
                self.workspace,
                self.user,
            ),
        )

    def test_long_model_ids_fit_their_columns(self):
        """Model ids are free-form configuration; a long one is a BYOK fact,
        not a reason to lose its charge.
        """
        built = BuiltModel(TestModel(), "x" * 150, "y" * 80)
        row = self.record(built, RunUsage())
        self.assertEqual((len(row.provider), len(row.model_name)), (50, 100))

    def test_a_failed_insert_is_logged_not_raised(self):
        built = BuiltModel(TestModel(), "claude-opus-4-6", "google-vertex")
        with (
            patch.object(AiUsage.objects, "acreate", side_effect=RuntimeError("down")),
            self.assertLogs("hexa.assistant.models", level="ERROR"),
        ):
            row = self.record(built, RunUsage())
        self.assertIsNone(row)
        self.assertEqual(AiUsage.objects.count(), 0)
