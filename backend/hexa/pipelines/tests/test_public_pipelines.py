from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from hexa.core.test import TestCase
from hexa.pipelines.models import (
    MissingPipelineConfiguration,
    Pipeline,
    PipelineRun,
    PipelineRunLogLevel,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
    PipelineVersion,
    PipelineVisibility,
    PublicRunInProgress,
)
from hexa.pipelines.permissions import publish_pipeline
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

SIMPLE_PARAMETERS = [
    {"code": "count", "name": "Count", "type": "int", "required": True},
    {"code": "label", "name": "Label", "type": "str", "default": "x"},
    {"code": "token", "name": "Token", "type": "secret"},
]
# What a visitor cannot fill in, with and without a fallback.
CONNECTION_WITH_DEFAULT = {
    "code": "dhis",
    "name": "DHIS2",
    "type": "dhis2",
    "required": True,
    "default": "dhis2-play",
}
DATASET_WITHOUT_DEFAULT = {
    "code": "dataset",
    "name": "Dataset",
    "type": "dataset",
    "required": True,
}
STR_WITH_CONNECTION_WIDGET = {
    "code": "org_unit",
    "name": "Org unit",
    "type": "str",
    "widget": "DHIS2_ORG_UNITS",
    "connection": "dhis",
    "default": "ou1",
}


class PublicPipelineTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(name="Public Org")
        cls.USER_OWNER = User.objects.create_user("owner@bluesquarehub.com", "pw")
        cls.USER_EDITOR = User.objects.create_user("editor@bluesquarehub.com", "pw")
        cls.USER_OUTSIDER = User.objects.create_user("out@bluesquarehub.com", "pw")
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_OWNER,
            role=OrganizationMembershipRole.OWNER,
        )
        cls.WORKSPACE = create_workspace(
            cls.USER_OWNER, name="WS", organization=cls.ORGANIZATION
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )

    def _pipeline(self, parameters=SIMPLE_PARAMETERS, config=None, **kwargs):
        kwargs.setdefault("code", f"p{Pipeline.objects.count()}")
        pipeline = Pipeline.objects.create(workspace=self.WORKSPACE, name="P", **kwargs)
        if parameters is not None:
            pipeline.upload_new_version(
                self.USER_OWNER,
                zipfile=b"",
                name="v1",
                parameters=parameters,
                config=config or {},
            )
        return pipeline

    def _public_pipeline(self, **kwargs):
        pipeline = self._pipeline(**kwargs)
        pipeline.visibility = PipelineVisibility.PUBLIC
        pipeline.save()
        return pipeline

    # --- permissions ---

    def test_publish_is_for_organization_admins_and_owners(self):
        pipeline = self._pipeline()
        self.assertTrue(publish_pipeline(self.USER_OWNER, pipeline))
        self.assertFalse(publish_pipeline(self.USER_EDITOR, pipeline))
        self.assertFalse(publish_pipeline(self.USER_OUTSIDER, pipeline))
        self.assertFalse(publish_pipeline(AnonymousUser(), pipeline))

    def test_visibility_defaults_to_workspace(self):
        self.assertEqual(self._pipeline().visibility, PipelineVisibility.WORKSPACE)

    # --- publishing ---

    def test_editor_cannot_publish_but_can_take_back(self):
        pipeline = self._pipeline()
        with self.assertRaises(PermissionDenied):
            pipeline.update_if_has_perm(
                self.USER_EDITOR, visibility=PipelineVisibility.PUBLIC
            )
        pipeline.update_if_has_perm(
            self.USER_OWNER, visibility=PipelineVisibility.PUBLIC
        )
        self.assertTrue(pipeline.is_public)
        pipeline.update_if_has_perm(
            self.USER_EDITOR, visibility=PipelineVisibility.WORKSPACE
        )
        self.assertFalse(pipeline.is_public)

    def test_echoing_the_current_visibility_needs_no_publish_right(self):
        pipeline = self._public_pipeline()
        pipeline.update_if_has_perm(
            self.USER_EDITOR, visibility=PipelineVisibility.PUBLIC, name="renamed"
        )
        self.assertEqual(pipeline.name, "renamed")

    def test_publishing_needs_a_version(self):
        pipeline = self._pipeline(parameters=None)
        with self.assertRaises(PipelineVersion.DoesNotExist):
            pipeline.update_if_has_perm(
                self.USER_OWNER, visibility=PipelineVisibility.PUBLIC
            )

    def test_publishing_needs_defaults_for_what_visitors_cannot_set(self):
        pipeline = self._pipeline(
            parameters=SIMPLE_PARAMETERS
            + [CONNECTION_WITH_DEFAULT, DATASET_WITHOUT_DEFAULT]
        )
        with self.assertRaises(MissingPipelineConfiguration) as ctx:
            pipeline.update_if_has_perm(
                self.USER_OWNER, visibility=PipelineVisibility.PUBLIC
            )
        self.assertEqual(ctx.exception.missing, ["dataset"])

        # A value in the version config is as good as a default.
        version = pipeline.last_version
        version.config = {"dataset": "ds"}
        version.save()
        pipeline.update_if_has_perm(
            self.USER_OWNER, visibility=PipelineVisibility.PUBLIC
        )
        self.assertTrue(pipeline.is_public)

    def test_optional_parameters_visitors_cannot_set_do_not_block(self):
        pipeline = self._pipeline(
            parameters=[{"code": "f", "name": "F", "type": "file", "required": False}]
        )
        self.assertEqual(pipeline.get_public_run_blockers(), [])
        self.assertTrue(pipeline.is_publicly_runnable)

    def test_notebook_pipelines_can_be_published(self):
        pipeline = self._pipeline(
            parameters=None, type=PipelineType.NOTEBOOK, notebook_path="nb.ipynb"
        )
        pipeline.update_if_has_perm(
            self.USER_OWNER, visibility=PipelineVisibility.PUBLIC
        )
        self.assertTrue(pipeline.is_publicly_runnable)
        self.assertEqual(pipeline.get_public_parameters(), [])

    # --- what the visitor sees ---

    def test_public_parameters_are_the_plain_ones(self):
        pipeline = self._public_pipeline(
            parameters=SIMPLE_PARAMETERS
            + [CONNECTION_WITH_DEFAULT, STR_WITH_CONNECTION_WIDGET]
        )
        self.assertEqual(
            [p["code"] for p in pipeline.get_public_parameters()],
            ["count", "label", "token"],
        )

    def test_a_new_version_can_make_a_public_pipeline_unrunnable(self):
        pipeline = self._public_pipeline()
        self.assertTrue(pipeline.is_publicly_runnable)
        pipeline.upload_new_version(
            self.USER_OWNER,
            zipfile=b"",
            name="v2",
            parameters=[DATASET_WITHOUT_DEFAULT],
        )
        self.assertFalse(pipeline.is_publicly_runnable)
        self.assertEqual(pipeline.get_public_run_blockers(), ["dataset"])

    def test_scheduled_version_is_the_one_visitors_run(self):
        pipeline = self._public_pipeline()
        v1 = pipeline.last_version
        pipeline.upload_new_version(
            self.USER_OWNER,
            zipfile=b"",
            name="v2",
            parameters=[DATASET_WITHOUT_DEFAULT],
        )
        pipeline.scheduled_pipeline_version = v1
        pipeline.save()
        self.assertTrue(pipeline.is_publicly_runnable)
        run = pipeline.run_public(AnonymousUser(), {"count": 1})
        self.assertEqual(run.pipeline_version, v1)

    # --- querysets ---

    def test_public_queryset(self):
        private = self._pipeline()
        public = self._public_pipeline()
        self.assertEqual(list(Pipeline.objects.public()), [public])
        # Membership-based access is untouched by visibility.
        self.assertNotIn(public, Pipeline.objects.filter_for_user(self.USER_OUTSIDER))
        self.assertIn(private, Pipeline.objects.filter_for_user(self.USER_EDITOR))

    # --- running ---

    def test_run_public_as_a_visitor(self):
        pipeline = self._public_pipeline(
            parameters=SIMPLE_PARAMETERS + [CONNECTION_WITH_DEFAULT]
        )
        run = pipeline.run_public(
            AnonymousUser(),
            # Nothing but the plain parameters gets through, whatever is sent.
            {"count": 3, "token": "s3cret", "dhis": "evil", "unknown": 1},
        )
        self.assertIsNone(run.user)
        self.assertEqual(run.trigger_mode, PipelineRunTrigger.PUBLIC)
        self.assertEqual(run.state, PipelineRunState.QUEUED)
        self.assertEqual(run.log_level, PipelineRunLogLevel.INFO)
        self.assertTrue(run.send_mail_notifications)
        # The stored config also carries the version's fallbacks for the rest.
        self.assertEqual(run.config["count"], 3)
        self.assertEqual(run.config["token"], "s3cret")
        self.assertEqual(run.config["dhis"], "dhis2-play")
        self.assertNotIn("unknown", run.config)

    def test_run_public_as_a_member_keeps_their_name(self):
        pipeline = self._public_pipeline()
        run = pipeline.run_public(self.USER_EDITOR, {"count": 1})
        self.assertEqual(run.user, self.USER_EDITOR)
        self.assertEqual(run.trigger_mode, PipelineRunTrigger.PUBLIC)

    def test_run_public_refuses_a_pipeline_that_is_not_public(self):
        pipeline = self._pipeline()
        with self.assertRaises(PermissionDenied):
            pipeline.run_public(AnonymousUser(), {"count": 1})

    def test_run_public_refuses_an_unrunnable_pipeline(self):
        pipeline = self._public_pipeline()
        pipeline.upload_new_version(
            self.USER_OWNER,
            zipfile=b"",
            name="v2",
            parameters=[DATASET_WITHOUT_DEFAULT],
        )
        with self.assertRaises(MissingPipelineConfiguration):
            pipeline.run_public(AnonymousUser(), {})

    def test_run_public_validates_the_values(self):
        pipeline = self._public_pipeline()
        with self.assertRaises(ValueError):
            pipeline.run_public(AnonymousUser(), {"count": "three"})

    def test_one_public_run_at_a_time(self):
        pipeline = self._public_pipeline()
        first = pipeline.run_public(AnonymousUser(), {"count": 1})
        with self.assertRaises(PublicRunInProgress):
            pipeline.run_public(AnonymousUser(), {"count": 2})
        # A member's own run does not hold the slot.
        pipeline.run(
            user=self.USER_EDITOR,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={"count": 1},
        )
        first.state = PipelineRunState.SUCCESS
        first.save()
        pipeline.run_public(AnonymousUser(), {"count": 3})

    def test_public_runs_queryset(self):
        pipeline = self._public_pipeline()
        public_run = pipeline.run_public(AnonymousUser(), {"count": 1})
        member_run = pipeline.run(
            user=self.USER_EDITOR,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={"count": 1},
        )
        self.assertEqual(list(PipelineRun.objects.public()), [public_run])
        self.assertEqual(list(PipelineRun.objects.filter_for_user(AnonymousUser())), [])
        self.assertEqual(
            list(
                PipelineRun.objects.filter_for_user(
                    AnonymousUser(), include_public=True
                )
            ),
            [public_run],
        )
        self.assertCountEqual(
            PipelineRun.objects.filter_for_user(self.USER_EDITOR, include_public=True),
            [public_run, member_run],
        )
        # Taking the pipeline back takes its public runs out of reach.
        pipeline.visibility = PipelineVisibility.WORKSPACE
        pipeline.save()
        self.assertEqual(list(PipelineRun.objects.public()), [])
