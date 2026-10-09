from django.apps import apps
from oauth2_provider.models import Application

from hexa.core.test import TestCase
from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile
from hexa.mcp.models import MCPConnection, MCPUser
from hexa.mcp.tests.testutils import all_tool_names
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Connection,
    ConnectionType,
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace


def querysets_filtered_for_user():
    managers = [
        (model, getattr(model, "objects", model._default_manager))
        for model in apps.get_models()
    ]
    return [
        (model, manager)
        for model, manager in managers
        if hasattr(manager, "filter_for_user")
    ]


class MCPAccessCeilingTest(TestCase):
    """Whatever an MCP connection is granted, it never reaches anything its
    person cannot: for every filter_for_user, the MCPUser's result is a subset
    of the person's. The fixture covers the cases that differ by kind of access:
    organization members and non-members, admins, viewers, superusers, and data
    that is linked, shared with an organization, private or shared.
    """

    @classmethod
    def setUpTestData(cls):
        cls.SUPERUSER = User.objects.create_user(
            "root@openhexa.org", "password", is_superuser=True
        )
        cls.ORG = Organization.objects.create(name="Org")
        cls.OTHER_ORG = Organization.objects.create(name="Other org")
        cls.W1 = create_workspace(cls.SUPERUSER, name="W1", organization=cls.ORG)
        cls.W2 = create_workspace(cls.SUPERUSER, name="W2", organization=cls.ORG)
        cls.W3 = create_workspace(cls.SUPERUSER, name="W3", organization=cls.OTHER_ORG)

        cls.WORKSPACE_EDITOR = cls.person(
            "editor@openhexa.org", {cls.W1: WorkspaceMembershipRole.EDITOR}
        )
        cls.ORG_MEMBER = cls.person(
            "member@openhexa.org",
            {cls.W2: WorkspaceMembershipRole.VIEWER},
            org_role=OrganizationMembershipRole.MEMBER,
        )
        cls.ORG_ADMIN = cls.person(
            "admin@openhexa.org", {}, org_role=OrganizationMembershipRole.ADMIN
        )
        cls.OUTSIDER = cls.person(
            "outsider@openhexa.org", {cls.W3: WorkspaceMembershipRole.ADMIN}
        )

        for workspace in (cls.W1, cls.W2, cls.W3):
            cls.populate(workspace)

        shared = Dataset.objects.get(workspace=cls.W2)
        shared.shared_with_organization = True
        shared.save()
        Dataset.objects.get(workspace=cls.W1).link(cls.SUPERUSER, cls.W3)
        for author, visibility in (
            (cls.SUPERUSER, SavedQueryVisibility.PRIVATE),
            (cls.WORKSPACE_EDITOR, SavedQueryVisibility.PRIVATE),
            (cls.WORKSPACE_EDITOR, SavedQueryVisibility.WORKSPACE),
        ):
            SavedQuery.objects.create_if_has_perm(
                author,
                cls.W1,
                name=f"{author.email} {visibility}",
                content="SELECT 1",
                visibility=visibility,
            )

        cls.APPLICATION = Application.objects.create(
            name="Claude",
            client_id="ceiling-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

    @classmethod
    def person(cls, email, workspaces, org_role=None):
        user = User.objects.create_user(email, "password")
        for workspace, role in workspaces.items():
            WorkspaceMembership.objects.create(
                user=user, workspace=workspace, role=role
            )
        if org_role:
            OrganizationMembership.objects.create(
                organization=cls.ORG, user=user, role=org_role
            )
        return user

    @classmethod
    def populate(cls, workspace):
        pipeline = Pipeline.objects.create(
            workspace=workspace, name=f"{workspace.name} pipeline", code="p"
        )
        version = PipelineVersion.objects.create(
            pipeline=pipeline, user=cls.SUPERUSER, zipfile=b"", parameters=[]
        )
        template = PipelineTemplate.objects.create(
            name=f"{workspace.name} template",
            code=f"{workspace.slug}-template",
            workspace=workspace,
            source_pipeline=pipeline,
        )
        PipelineTemplateVersion.objects.create(
            template=template,
            version_number=1,
            user=cls.SUPERUSER,
            source_pipeline_version=version,
        )
        dataset = Dataset.objects.create_if_has_perm(
            cls.SUPERUSER, workspace, name=f"{workspace.name} dataset", description=""
        )
        dataset_version = DatasetVersion.objects.create_if_has_perm(
            cls.SUPERUSER, dataset=dataset, name="v1", changelog=""
        )
        DatasetVersionFile.objects.create_if_has_perm(
            cls.SUPERUSER,
            dataset_version=dataset_version,
            uri=f"{workspace.slug}/file.csv",
            content_type="text/csv",
        )
        Webapp.objects.create(
            name=f"{workspace.name} app",
            slug=f"{workspace.slug}-app",
            subdomain=f"{workspace.slug}-app",
            workspace=workspace,
            created_by=cls.SUPERUSER,
        )
        Connection.objects.create_if_has_perm(
            cls.SUPERUSER,
            workspace=workspace,
            name=f"{workspace.name} connection",
            slug=f"{workspace.slug}-connection",
            connection_type=ConnectionType.CUSTOM,
        )

    def fully_granted(self, user):
        connection = MCPConnection.objects.create(
            user=user, application=self.APPLICATION, tools=all_tool_names()
        )
        connection.workspaces.set(Workspace.objects.all())
        return MCPUser.from_user(user, connection)

    def test_an_mcp_user_never_reaches_more_than_its_person(self):
        people = (
            self.WORKSPACE_EDITOR,
            self.ORG_MEMBER,
            self.ORG_ADMIN,
            self.OUTSIDER,
            self.SUPERUSER,
        )
        querysets = querysets_filtered_for_user()
        checked = 0
        for user in people:
            mcp_user = self.fully_granted(user)
            for model, manager in querysets:
                try:
                    allowed = set(
                        manager.filter_for_user(user).values_list("pk", flat=True)
                    )
                except NotImplementedError:
                    continue
                reached = set(
                    manager.filter_for_user(mcp_user).values_list("pk", flat=True)
                )
                checked += 1
                with self.subTest(person=user.email, model=model._meta.label):
                    self.assertEqual(set(), reached - allowed)
        self.assertGreater(checked, 0)
