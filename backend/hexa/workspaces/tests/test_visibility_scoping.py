"""A workspace token must not see past its workspace.

Nearly every workspace-owned queryset reaches access control through
`Workspace.objects.filter_for_user`, so narrowing that one method scopes the lot.
This test asserts the narrowing at the choke point and, one model at a time, that
it really does cascade — and it runs everything twice, because a superuser takes
shortcuts (`self.all()`, `return_all_if_superuser`) that skip the branches an
ordinary user goes through.

Each assertion is an equality, so it fails both when something out of scope stays
visible and when something in scope stops being visible.
"""

from hexa.data_studio.models import SavedQuery
from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import Organization
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Connection, Workspace, WorkspaceMembership
from hexa.workspaces.tests.testutils import WorkspaceScopingTestCase

# Workspace-owned models whose `filter_for_user` must resolve to the scope alone.
# Spelled out rather than discovered: this is the list of things a token can read,
# and it should be reviewed when it changes.
SCOPED_MODELS = [
    Workspace,
    WorkspaceMembership,
    Connection,
    Pipeline,
    PipelineVersion,
    PipelineTemplate,
    PipelineTemplateVersion,
    Dataset,
    DatasetVersion,
    DatasetVersionFile,
    DatasetLink,
    Webapp,
    SavedQuery,
]


class WorkspaceVisibilityScopingTest(WorkspaceScopingTestCase):
    maxDiff = None

    def assertOnlyVisible(self, queryset, expected, what):
        self.assertEqual(
            {expected},
            set(queryset),
            f"{what} is not scoped to the token's workspace",
        )

    def assertScoped(self, queryset, model, what):
        """Asserted per object rather than by equality: some models have several
        rows in scope (two pipeline versions), and naming them all would say less
        than the two things that matter.
        """
        visible = set(queryset)
        self.assertIn(
            self.IN_SCOPE_OBJECTS[model],
            visible,
            f"{what} hides an object in the token's own workspace",
        )
        self.assertNotIn(
            self.OUT_OF_SCOPE_OBJECTS[model],
            visible,
            f"{what} exposes an object from another workspace",
        )

    def test_only_the_scoped_workspace_is_visible(self):
        for user in (self.USER, self.SUPERUSER):
            with self.subTest(holder=user.email):
                principal = self.scoped_principal(user)
                self.assertOnlyVisible(
                    Workspace.objects.filter_for_user(principal),
                    self.IN_SCOPE,
                    "Workspace.filter_for_user",
                )

    def test_only_the_scoped_workspace_is_visible_by_slug(self):
        """`filter_for_workspace_slugs` has its own superuser shortcut to narrow."""
        slugs = [self.IN_SCOPE.slug, self.OUT_OF_SCOPE.slug]
        for user in (self.USER, self.SUPERUSER):
            with self.subTest(holder=user.email):
                principal = self.scoped_principal(user)
                self.assertOnlyVisible(
                    Workspace.objects.filter_for_workspace_slugs(principal, slugs),
                    self.IN_SCOPE,
                    "Workspace.filter_for_workspace_slugs",
                )

    def test_only_workspace_owned_objects_in_scope_are_visible(self):
        for user in (self.USER, self.SUPERUSER):
            for model in SCOPED_MODELS:
                with self.subTest(holder=user.email, model=model.__name__):
                    principal = self.scoped_principal(user)
                    self.assertScoped(
                        model.objects.filter_for_user(principal),
                        model,
                        f"{model.__name__}.filter_for_user",
                    )

    def test_only_the_organization_owning_the_scoped_workspace_is_visible(self):
        """The organization is reachable as a sharing boundary, not as an entity.

        It has to stay visible for organization-shared datasets to keep working,
        but only the one that owns the token's workspace: the holder is an owner
        of another organization too, and the token grants nothing there.
        """
        for user in (self.USER, self.SUPERUSER):
            for direct_only in (False, True):
                with self.subTest(
                    holder=user.email, direct_membership_only=direct_only
                ):
                    principal = self.scoped_principal(user)
                    self.assertOnlyVisible(
                        Organization.objects.filter_for_user(
                            principal, direct_membership_only=direct_only
                        ),
                        self.ORGANIZATION,
                        "Organization.filter_for_user",
                    )
