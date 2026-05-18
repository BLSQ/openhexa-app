from django.test import TestCase

from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.authentication import WebappUser
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class WebappUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORG_A = Organization.objects.create(name="Org A", short_name="org-a")
        cls.ORG_B = Organization.objects.create(name="Org B", short_name="org-b")

        cls.MEMBER = User.objects.create_user("member@test.com", "p")
        cls.OUTSIDER = User.objects.create_user("outsider@test.com", "p")

        cls.WORKSPACE = Workspace.objects.create(
            name="App WS", slug="app-ws", db_name="app_ws_db", organization=cls.ORG_A
        )
        cls.OTHER_WORKSPACE = Workspace.objects.create(
            name="Other WS",
            slug="other-ws",
            db_name="other_ws_db",
            organization=cls.ORG_B,
        )
        WorkspaceMembership.objects.create(
            user=cls.MEMBER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            user=cls.MEMBER,
            organization=cls.ORG_A,
            role=OrganizationMembershipRole.ADMIN,
        )
        # OUTSIDER is in Org A but only as a member, with no workspace membership.
        OrganizationMembership.objects.create(
            user=cls.OUTSIDER,
            organization=cls.ORG_A,
            role=OrganizationMembershipRole.MEMBER,
        )

        cls.WEBAPP = Webapp.objects.create(
            name="App",
            slug="app",
            subdomain="app",
            url="http://example.com",
            workspace=cls.WORKSPACE,
            created_by=cls.MEMBER,
            is_public=False,
            allowed_operations=[
                Webapp.OperationScope.DATASETS_WRITE,
                Webapp.OperationScope.PIPELINES_RUN,
            ],
        )

    # accessible_workspaces ---------------------------------------------------

    def test_public_webapp_hard_scopes_to_its_workspace(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=None)
        self.assertEqual(
            list(principal.accessible_workspaces().values_list("pk", flat=True)),
            [self.WORKSPACE.pk],
        )

    def test_private_webapp_intersects_with_real_user(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=self.MEMBER)
        self.assertEqual(
            list(principal.accessible_workspaces().values_list("pk", flat=True)),
            [self.WORKSPACE.pk],
        )

    def test_private_webapp_returns_empty_if_real_user_has_no_access(self):
        # OUTSIDER is only an Org A *member* (not admin) and has no direct
        # WorkspaceMembership → cannot reach this workspace via accessible_workspaces.
        principal = WebappUser(webapp=self.WEBAPP, real_user=self.OUTSIDER)
        self.assertEqual(list(principal.accessible_workspaces()), [])

    # accessible_organizations ------------------------------------------------

    def test_public_webapp_organizations_is_the_workspace_org(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=None)
        self.assertEqual(
            list(principal.accessible_organizations().values_list("pk", flat=True)),
            [self.ORG_A.pk],
        )

    def test_private_webapp_organizations_intersects_real_user_orgs(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=self.MEMBER)
        self.assertEqual(
            list(principal.accessible_organizations().values_list("pk", flat=True)),
            [self.ORG_A.pk],
        )

    # has_perm ----------------------------------------------------------------

    def test_public_webapp_has_perm_always_denies(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=None)
        self.assertFalse(
            principal.has_perm("datasets.create_dataset", self.WORKSPACE)
        )

    def test_private_webapp_has_perm_gates_by_allowed_operations(self):
        # FILES_READ is NOT in self.WEBAPP.allowed_operations, so even if the
        # real user could download, the webapp principal must deny.
        principal = WebappUser(webapp=self.WEBAPP, real_user=self.MEMBER)
        self.assertFalse(
            principal.has_perm("files.download_object", self.WORKSPACE)
        )

    def test_private_webapp_has_perm_allows_when_scope_granted(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=self.MEMBER)
        # MEMBER is workspace ADMIN → can create datasets; DATASETS_WRITE is granted.
        self.assertTrue(
            principal.has_perm("datasets.create_dataset", self.WORKSPACE)
        )

    def test_unregistered_perm_is_denied(self):
        # A perm name that no scope maps to should fail-closed even when the
        # real user has it. (Adding a new webapp-reachable perm requires
        # registering it in hexa.webapps.scopes.)
        principal = WebappUser(webapp=self.WEBAPP, real_user=self.MEMBER)
        self.assertFalse(
            principal.has_perm("workspaces.update_workspace", self.WORKSPACE)
        )

    # human_actor -------------------------------------------------------------

    def test_human_actor_is_real_user_for_private(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=self.MEMBER)
        self.assertEqual(principal.human_actor, self.MEMBER)

    def test_human_actor_is_none_for_public(self):
        principal = WebappUser(webapp=self.WEBAPP, real_user=None)
        self.assertIsNone(principal.human_actor)

    # can_create_in_workspace -------------------------------------------------

    def test_cannot_bypass_perm_check(self):
        # WebappUser must NOT bypass has_perm — pipeline-run-style bypass is
        # reserved for PipelineRunUser. WebappUser writes flow through has_perm.
        private = WebappUser(webapp=self.WEBAPP, real_user=self.MEMBER)
        public = WebappUser(webapp=self.WEBAPP, real_user=None)
        self.assertFalse(private.can_create_in_workspace(self.WORKSPACE))
        self.assertFalse(public.can_create_in_workspace(self.WORKSPACE))
