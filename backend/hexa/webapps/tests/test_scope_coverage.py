from django.test import SimpleTestCase
from graphql import (
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLUnionType,
    get_named_type,
)

from config.schema import schema
from hexa.webapps.scopes import SCOPE_GRANTS, _merge

# Fields deliberately kept out of every scope, on types a web app can reach. This
# list is never read at runtime (anything outside SCOPE_GRANTS is refused anyway):
# it lets the test below tell a refused field from one nobody has looked at yet.
NEVER_GRANTED = {
    # Edges back up to a workspace or the organization lead out of the web app's
    # workspace, to connections, credentials and other workspaces' data.
    "Dataset": {"workspace"},
    "DatasetLink": {"workspace"},
    "WorkspaceMembership": {"workspace", "organizationMembership", "user"},
    "Organization": {
        "workspaces",
        "datasets",
        "datasetLinks",
        "members",
        "externalCollaborators",
        "invitations",
        "pendingWorkspaceInvitations",
        "permissions",
        "workspaceTags",
        "pipelineTags",
        "pipelineTemplateTags",
        "usage",
        "subscription",
        "aiSettings",
        "aiBudgetLimitReached",
        "contactInfo",
    },
    # Secrets, people and resources with no scope of their own.
    "Workspace": {
        "connections",
        "configuration",
        "database",
        "dockerImage",
        "members",
        "invitations",
        "savedQueries",
        "shortcuts",
        "assistantConversations",
        "pipelineTemplateTags",
    },
    "Pipeline": {
        "workspace",
        "webhookUrl",
        "recipients",
        "assistantConversations",
        "template",
        "sourceTemplate",
        "newTemplateVersions",
    },
    # Pipeline source code.
    "PipelineVersion": {"zipfile", "files", "dag", "templateVersion"},
    # Table content is only readable through DATABASE_READ's saved queries.
    "DatabaseTable": {"rows", "sample"},
    "DatasetVersionFile": {"uri"},
    "User": {"lastLogin", "dateJoined", "analyticsEnabled"},
    "Me": {
        "hasTwoFactorEnabled",
        "assistantMonthlyCost",
        "assistantMonthlyLimitExceeded",
        "assistantTotalCost",
    },
}


def _object_types(graphql_type) -> list[GraphQLObjectType]:
    if isinstance(graphql_type, GraphQLUnionType):
        return list(graphql_type.types)
    if isinstance(graphql_type, GraphQLInterfaceType):
        return list(schema.get_implementations(graphql_type).objects)
    if isinstance(graphql_type, GraphQLObjectType):
        return [graphql_type]
    return []


class ScopeCoverageTest(SimpleTestCase):
    allowed = _merge(*(grant.fields for grant in SCOPE_GRANTS.values()))

    def _reachable_types(self) -> set[str]:
        seen, stack = set(), [schema.query_type, schema.mutation_type]
        while stack:
            graphql_type = stack.pop()
            if graphql_type.name in seen:
                continue
            seen.add(graphql_type.name)
            for field_name in self.allowed.get(graphql_type.name, ()):
                field_type = get_named_type(graphql_type.fields[field_name].type)
                stack.extend(_object_types(field_type))
        return seen - {schema.query_type.name, schema.mutation_type.name}

    def test_every_reachable_field_is_classified(self):
        unclassified = {
            f"{type_name}.{field_name}"
            for type_name in self._reachable_types()
            for field_name in schema.get_type(type_name).fields
            if field_name not in self.allowed.get(type_name, ())
            and field_name not in NEVER_GRANTED.get(type_name, ())
        }
        self.assertEqual(
            unclassified,
            set(),
            "Web apps can reach these fields but they are neither granted in "
            "SCOPE_GRANTS nor listed in NEVER_GRANTED: decide which side they go on.",
        )

    def test_never_granted_fields_are_not_granted(self):
        overlap = {
            f"{type_name}.{field_name}"
            for type_name, fields in NEVER_GRANTED.items()
            for field_name in fields & self.allowed.get(type_name, set())
        }
        self.assertEqual(overlap, set())
