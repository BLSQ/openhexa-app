from hexa.assistant.evals.fixtures import (
    PROFILES,
    STANDARD_WORKSPACE,
    build_profile,
)
from hexa.assistant.evals.suites.pipeline_create.task import (
    EVAL_CONVERSATION_NAME,
    _build_world,
)
from hexa.core.test import TestCase
from hexa.mcp.tools.connections import list_connections
from hexa.mcp.tools.datasets import list_datasets
from hexa.user_management.models import AiSettings, User


class FixtureProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "eval@openhexa.org", "password", is_superuser=True
        )

    def test_unknown_profile_fails_loudly(self):
        with self.assertRaises(KeyError) as ctx:
            build_profile("dhis2_workspce", self.USER)
        self.assertIn(STANDARD_WORKSPACE, str(ctx.exception))

    def test_every_profile_builds(self):
        for name in PROFILES:
            with self.subTest(profile=name):
                world = build_profile(name, self.USER)
                self.assertIsNotNone(world.workspace.slug)

    def test_standard_workspace_spec_matches_seeded_objects(self):
        world = build_profile(STANDARD_WORKSPACE, self.USER)
        self.assertEqual(
            {"dhis2-play", "dhis2-target", "iaso-staging", "cds-climate"},
            set(world.spec.connection_slugs),
        )
        self.assertEqual(
            {"boundaries", "analytics-output"}, set(world.spec.dataset_slugs)
        )
        self.assertIn("data/mapping.csv", world.spec.file_paths)

    def test_agent_tools_see_the_seeded_world(self):
        """The spec must describe what the agent's discovery tools actually return.

        If these drift apart, the grounding verifier judges the agent against a
        world it was never shown.
        """
        world = build_profile(STANDARD_WORKSPACE, self.USER)
        slug = world.workspace.slug

        connections = list_connections(user=self.USER, workspace_slug=slug)
        self.assertEqual(
            set(world.spec.connection_slugs),
            {c["slug"] for c in connections["connections"]},
        )

        datasets = list_datasets(user=self.USER, workspace_slug=slug)
        self.assertEqual(
            set(world.spec.dataset_slugs),
            {d["slug"] for d in datasets["datasets"]["items"]},
        )

    def test_profiles_are_isolated_from_each_other(self):
        """Each repeat gets a fresh workspace; state must not leak between runs."""
        first = build_profile(STANDARD_WORKSPACE, self.USER)
        second = build_profile(STANDARD_WORKSPACE, self.USER)
        self.assertNotEqual(first.workspace.pk, second.workspace.pk)
        self.assertEqual(
            4,
            list_connections(user=self.USER, workspace_slug=second.workspace.slug)[
                "connections"
            ].__len__(),
        )


class EvalConversationTest(TestCase):
    """The conversation the agent runs in, not the world it runs against."""

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "eval-conv@openhexa.org", "password", is_superuser=True
        )

    def test_conversation_is_pre_named_to_skip_the_naming_agent(self):
        """run_stream only titles a conversation whose name is None.

        Leaving it unnamed spends a second model round-trip per case on work
        that is not under test, and folds its usage into the case's cost.
        """
        _, conversation = _build_world(STANDARD_WORKSPACE)
        self.assertEqual(EVAL_CONVERSATION_NAME, conversation.name)

    def test_ai_settings_use_the_managed_provider(self):
        """Evals standardise on Vertex, the transport production runs on."""
        _, conversation = _build_world(STANDARD_WORKSPACE)
        ai_settings = conversation.workspace.organization.ai_settings
        self.assertTrue(ai_settings.enabled)
        self.assertEqual(AiSettings.Provider.MANAGED, ai_settings.provider)

    def test_managed_settings_carry_no_key(self):
        """Vertex authenticates with ambient credentials, not a stored key.

        AiModelBuilder discards both fields for managed orgs, so leaving them
        null keeps the row honest about what actually drives the run.
        """
        _, conversation = _build_world(STANDARD_WORKSPACE)
        ai_settings = conversation.workspace.organization.ai_settings
        self.assertIsNone(ai_settings.model)
        self.assertFalse(ai_settings.has_api_key)
