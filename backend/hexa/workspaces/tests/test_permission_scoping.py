"""A workspace token must act as its owner inside its workspace, and as nobody outside it.

Permissions are discovered the way `PermissionsBackend` discovers them, so a new
permission function is covered the moment it is written, and the object to test
each one with comes from the annotation of its second parameter. A permission
whose object type has no fixture here fails as UNCLASSIFIED rather than passing
silently — that is what keeps "scoped by default" true over time.

The principal is deliberately the most privileged one that can hold a token:
admin of both workspaces *and* owner of the organization that owns them. Every
authority a permission can appeal to says yes, so only the scope can say no.
"""

import inspect
import typing
from importlib import import_module
from unittest.mock import patch

from django.apps import apps
from django.test import TestCase

from hexa.data_studio.models import SavedQuery
from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    Team,
    User,
)
from hexa.webapps.models import Webapp
from hexa.workspaces.authentication import WorkspaceToken
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceTokenUser,
)
from hexa.workspaces.tests.testutils import create_workspace

# Connector plugins predate workspaces and own resources no workspace token should
# reach at all. They are shut out by the endpoint and GraphQL allowlists rather
# than by workspace scoping, so their permissions are out of scope for this test.
# Listed one by one so that a *new* app is never silently exempt.
UNSCOPED_APP_LABELS = {
    "connector_accessmod",
    "connector_airflow",
    "connector_dhis2",
    "connector_postgresql",
    "connector_s3",
}


def discover_permissions() -> list[tuple[str, str, typing.Callable]]:
    """Every (app_label, name, function) the permissions backend can resolve.

    Mirrors `PermissionsBackend._get_permission_module`, including its "only
    hexa.* apps" rule, so discovery cannot drift from dispatch.
    """
    found = []
    for app_config in apps.get_app_configs():
        if not app_config.name.startswith("hexa."):
            continue
        if app_config.label in UNSCOPED_APP_LABELS:
            continue
        try:
            module = import_module(f"{app_config.name}.permissions")
        except ModuleNotFoundError:
            continue
        for name, function in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_") or function.__module__ != module.__name__:
                continue
            found.append((app_config.label, name, function))
    return sorted(found)


def permission_object_type(function: typing.Callable) -> type | None:
    """The type of object a permission is asked about, or None if it takes none."""
    parameters = list(inspect.signature(function).parameters.values())[1:]
    if not parameters:
        return None
    return typing.get_type_hints(function).get(parameters[0].name, object)


class WorkspacePermissionScopingTest(TestCase):
    # The failures list every offending permission; truncating them hides the point.
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(name="Scoping Organization")
        cls.USER = User.objects.create_user("holder@openhexa.org", "Pa$$w0rd")
        cls.OTHER_USER = User.objects.create_user("other@openhexa.org", "Pa$$w0rd")
        cls.SUPERUSER = User.objects.create_user(
            "root@openhexa.org", "Pa$$w0rd", is_superuser=True
        )
        for user in (cls.USER, cls.SUPERUSER):
            OrganizationMembership.objects.create(
                organization=cls.ORGANIZATION,
                user=user,
                role=OrganizationMembershipRole.OWNER,
            )

        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            # create_if_has_perm provisions the slug and an ADMIN membership for
            # the creator, in both workspaces.
            cls.IN_SCOPE = create_workspace(
                cls.USER, name="In Scope", organization=cls.ORGANIZATION
            )
            # Same organization on purpose: a workspace in another organization
            # would also be refused by the organization checks, and so would
            # never exercise the scope itself.
            cls.OUT_OF_SCOPE = create_workspace(
                cls.USER, name="Out Of Scope", organization=cls.ORGANIZATION
            )

        cls.IN_SCOPE_OBJECTS = cls.build_workspace_objects(cls.IN_SCOPE, "in")
        cls.OUT_OF_SCOPE_OBJECTS = cls.build_workspace_objects(cls.OUT_OF_SCOPE, "out")
        cls.BEYOND_SCOPE_OBJECTS = cls.build_beyond_scope_objects()

    @classmethod
    def build_workspace_objects(cls, workspace: Workspace, prefix: str) -> dict:
        """One object of each workspace-owned permission object type, in `workspace`.

        Fixtures are shaped so that no permission is refused for a reason other
        than scope: two pipeline versions because `delete_pipeline_version` needs
        more than one, two template versions for the same reason, and the dataset
        version the file hangs off is the dataset's latest.
        """
        pipeline = Pipeline.objects.create(
            workspace=workspace, name=f"{prefix} pipeline", code=f"{prefix}-pipeline"
        )
        versions = [
            PipelineVersion.objects.create(
                pipeline=pipeline, user=cls.USER, version_number=number
            )
            for number in (1, 2)
        ]
        template = PipelineTemplate.objects.create(
            workspace=workspace, name=f"{prefix} template", source_pipeline=pipeline
        )
        template_versions = [
            PipelineTemplateVersion.objects.create(
                template=template,
                version_number=number,
                source_pipeline_version=version,
            )
            for number, version in enumerate(versions, start=1)
        ]

        dataset = Dataset.objects.create(
            workspace=workspace,
            created_by=cls.USER,
            name=f"{prefix} dataset",
            slug=f"{prefix}-dataset",
        )
        dataset_version = DatasetVersion.objects.create(
            dataset=dataset, name="v1", created_by=cls.USER
        )
        dataset_version_file = DatasetVersionFile.objects.create(
            dataset_version=dataset_version,
            uri=f"{prefix}/v1/file.csv",
            content_type="text/csv",
            created_by=cls.USER,
        )

        return {
            Workspace: workspace,
            Pipeline: pipeline,
            PipelineVersion: versions[-1],
            PipelineTemplate: template,
            PipelineTemplateVersion: template_versions[-1],
            Dataset: dataset,
            DatasetVersion: dataset_version,
            DatasetVersionFile: dataset_version_file,
            DatasetLink: DatasetLink.objects.create(
                dataset=dataset, workspace=workspace, created_by=cls.USER
            ),
            Connection: Connection.objects.create(
                workspace=workspace,
                user=cls.USER,
                name=f"{prefix} connection",
                slug=f"{prefix}-connection",
                connection_type=ConnectionType.CUSTOM,
            ),
            Webapp: Webapp.objects.create(
                workspace=workspace,
                created_by=cls.USER,
                name=f"{prefix} webapp",
                slug=f"{prefix}-webapp",
                subdomain=f"{prefix}-webapp",
            ),
            SavedQuery: SavedQuery.objects.create(
                workspace=workspace,
                created_by=cls.USER,
                name=f"{prefix} query",
                slug=f"{prefix}-query",
                content="SELECT 1",
            ),
            # `link_dataset` is asked about an unannotated (dataset, workspace) pair.
            "datasets.link_dataset": (dataset, workspace),
        }

    @classmethod
    def build_beyond_scope_objects(cls) -> dict:
        """Objects for the permissions that are not about a workspace at all.

        The organization here is the one that owns the *scoped* workspace, not a
        foreign one: organization-level power is out of a token's reach even
        where its own workspace lives. The token holder administers the team, so
        team permissions are not refused for lack of a role, and the membership
        under test belongs to somebody else, so `delete_membership` is not
        refused merely for being reflexive.
        """
        team = Team.objects.create(name="Beyond Scope Team")
        Membership.objects.create(team=team, user=cls.USER, role=MembershipRole.ADMIN)
        return {
            Organization: cls.ORGANIZATION,
            Team: team,
            Membership: Membership.objects.create(
                team=team, user=cls.OTHER_USER, role=MembershipRole.REGULAR
            ),
        }

    def scoped_principal(self, user: User) -> WorkspaceTokenUser:
        """The principal a token issued to `user` for the scoped workspace installs."""
        return WorkspaceTokenUser.from_token(
            WorkspaceToken.issue(
                user=user,
                workspace=self.IN_SCOPE,
                membership=self.IN_SCOPE.get_membership(user),
            )
        )

    def resolve(self, permissions, objects):
        """Pair each permission with its fixture, failing on any it cannot classify."""
        pairs, unclassified = [], []
        for app_label, name, function in permissions:
            permission = f"{app_label}.{name}"
            object_type = permission_object_type(function)
            if permission in objects:
                pairs.append((permission, objects[permission]))
            elif object_type in objects:
                pairs.append((permission, objects[object_type]))
            else:
                unclassified.append(f"{permission} (object: {object_type})")
        self.assertEqual(
            [],
            unclassified,
            "these permissions take an object this test has no fixture for, so "
            "their scoping is unverified — add one to build_workspace_objects "
            "or build_beyond_scope_objects",
        )
        return pairs

    def workspace_permissions(self, objects):
        """Permissions about a workspace-owned object, paired with their fixture."""
        return self.resolve(
            [
                permission
                for permission in discover_permissions()
                if permission_object_type(permission[2]) in self.IN_SCOPE_OBJECTS
                or f"{permission[0]}.{permission[1]}" in self.IN_SCOPE_OBJECTS
            ],
            objects,
        )

    def beyond_scope_permissions(self):
        """Permissions about an organization, a team, or nothing at all."""
        return [
            (f"{app_label}.{name}", self.BEYOND_SCOPE_OBJECTS.get(object_type))
            for app_label, name, function in discover_permissions()
            if (object_type := permission_object_type(function)) is None
            or object_type in self.BEYOND_SCOPE_OBJECTS
        ]

    def assertNoneGranted(self, principal, pairs, message):
        granted = [
            permission
            for permission, obj in pairs
            if principal.has_perm(permission, obj)
        ]
        self.assertEqual([], granted, message)

    def test_denies_workspace_permissions_outside_the_token_workspace(self):
        pairs = self.workspace_permissions(self.OUT_OF_SCOPE_OBJECTS)
        self.assertNotEqual([], pairs, "permission discovery found nothing")
        self.assertNoneGranted(
            self.scoped_principal(self.USER),
            pairs,
            "a workspace token granted these permissions on another workspace",
        )

    def test_denies_workspace_permissions_outside_a_superuser_token_workspace(self):
        """A superuser's token is not a master key.

        ModelBackend sits ahead of PermissionsBackend and answers True to every
        permission for a superuser, so this is only ever refused if the principal
        itself refuses before the backends are consulted.
        """
        self.assertNoneGranted(
            self.scoped_principal(self.SUPERUSER),
            self.workspace_permissions(self.OUT_OF_SCOPE_OBJECTS),
            "a superuser's workspace token granted these permissions on another "
            "workspace",
        )

    def test_denies_permissions_that_are_not_about_a_workspace(self):
        """Organization and team power is beyond any workspace token's reach.

        Scoping the workspace alone does not cover these: the token holder really
        is an owner of the organization their workspace belongs to.
        """
        pairs = self.beyond_scope_permissions()
        self.assertNotEqual([], pairs, "no organization or team permissions found")
        for user in (self.USER, self.SUPERUSER):
            with self.subTest(holder=user.email):
                self.assertNoneGranted(
                    self.scoped_principal(user),
                    pairs,
                    "a workspace token granted these organization or team "
                    "permissions",
                )

    def test_matches_its_owner_inside_the_token_workspace(self):
        """Scoping must subtract reach, not capability.

        Without this, refusing everything everywhere would satisfy the tests
        above. The reference is the same user unscoped, so the expectation
        follows the permission layer instead of a list to keep up to date.
        """
        principal = self.scoped_principal(self.USER)
        reference = User.objects.get(pk=self.USER.pk)

        lost = [
            permission
            for permission, obj in self.workspace_permissions(self.IN_SCOPE_OBJECTS)
            if reference.has_perm(permission, obj)
            and not principal.has_perm(permission, obj)
        ]
        self.assertEqual(
            [],
            lost,
            "a workspace token lost these permissions inside its own workspace",
        )
