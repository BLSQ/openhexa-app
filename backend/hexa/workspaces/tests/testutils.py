from unittest.mock import patch

from django.test import TestCase

from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.datasets.models import (
    Dataset,
    DatasetLink,
    DatasetVersion,
    DatasetVersionFile,
)
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.models import Webapp
from hexa.workspaces.authentication import WorkspaceToken
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceTokenUser,
)


def create_workspace(
    principal: User | None = None,
    *,
    name: str = "Test Workspace",
    organization: Organization | None = None,
    **kwargs,
) -> Workspace:
    """Create a Workspace (and, if needed, its Organization) for tests.

    Workspaces always belong to an organization, so tests that don't care about
    the organization can omit it and get a default one. Pass ``principal`` to go
    through ``create_if_has_perm`` (which also provisions the database/bucket, so
    callers usually patch those); omit it for a plain ``create``.
    """
    if organization is None:
        organization = Organization.objects.create(name=f"{name} Organization")
    if principal is not None:
        return Workspace.objects.create_if_has_perm(
            principal, name=name, organization=organization, **kwargs
        )
    return Workspace.objects.create(name=name, organization=organization, **kwargs)


class WorkspaceScopingTestCase(TestCase):
    """Fixtures for testing what a workspace-scoped principal may reach.

    Two workspaces in one organization, each holding one object of every
    workspace-owned type, plus a second organization. The token holder is as
    privileged as a token holder can be — admin of both workspaces and owner of
    both organizations — so that anything they cannot reach is the scope's doing
    and nothing else's.
    """

    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(name="Scoping Organization")
        cls.OTHER_ORGANIZATION = Organization.objects.create(name="Other Organization")
        cls.USER = User.objects.create_user("holder@openhexa.org", "Pa$$w0rd")
        cls.OTHER_USER = User.objects.create_user("other@openhexa.org", "Pa$$w0rd")
        cls.SUPERUSER = User.objects.create_user(
            "root@openhexa.org", "Pa$$w0rd", is_superuser=True
        )
        for organization in (cls.ORGANIZATION, cls.OTHER_ORGANIZATION):
            for user in (cls.USER, cls.SUPERUSER):
                OrganizationMembership.objects.create(
                    organization=organization,
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

    @classmethod
    def build_workspace_objects(cls, workspace: Workspace, prefix: str) -> dict:
        """One object of each workspace-owned type, in `workspace`, keyed by type.

        Fixtures are shaped so that nothing is refused for a reason other than
        scope: two pipeline versions because `delete_pipeline_version` needs more
        than one, two template versions for the same reason, and the dataset
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

        return {
            Workspace: workspace,
            Pipeline: pipeline,
            PipelineVersion: versions[-1],
            PipelineTemplate: template,
            PipelineTemplateVersion: template_versions[-1],
            Dataset: dataset,
            DatasetVersion: dataset_version,
            DatasetVersionFile: DatasetVersionFile.objects.create(
                dataset_version=dataset_version,
                uri=f"{prefix}/v1/file.csv",
                content_type="text/csv",
                created_by=cls.USER,
            ),
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
            # Visible to the whole workspace, so that what this fixture measures
            # is the workspace scope rather than who authored it.
            SavedQuery: SavedQuery.objects.create(
                workspace=workspace,
                created_by=cls.USER,
                name=f"{prefix} query",
                slug=f"{prefix}-query",
                content="SELECT 1",
                visibility=SavedQueryVisibility.WORKSPACE,
            ),
            WorkspaceMembership: workspace.get_membership(cls.USER),
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
