import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import hexa.user_management.models

MCP_SCOPE = "openhexa:mcp"

ALL_TOOLS = [
    "list_connections",
    "get_db_schema",
    "get_db_table_schema",
    "list_datasets",
    "get_dataset",
    "preview_dataset_file",
    "create_dataset",
    "create_dataset_version",
    "list_files",
    "read_file",
    "write_file",
    "list_pipelines",
    "get_pipeline",
    "get_pipeline_run",
    "run_pipeline",
    "update_pipeline",
    "create_pipeline",
    "create_pipeline_version",
    "list_pipeline_templates",
    "get_pipeline_template",
    "create_pipeline_from_template",
    "list_static_webapps",
    "get_static_webapp",
    "create_static_webapp",
    "update_static_webapp",
    "edit_static_webapp_file",
    "get_static_webapp_file",
    "list_workspaces",
    "get_workspace",
    "update_workspace",
]


def mcp_token_owners(apps):
    """The (user, application) pairs that already hold an MCP token.

    Keyed on foreign keys — never on the application name, which comes straight
    from the dynamic registration payload.
    """
    AccessToken = apps.get_model("oauth2_provider", "AccessToken")
    return set(
        AccessToken.objects.filter(
            scope__contains=MCP_SCOPE,
            user__isnull=False,
            application__isnull=False,
        ).values_list("user_id", "application_id")
    )


def reachable_workspaces(apps, user_ids):
    """The workspaces each of these users can reach, as {user_id: {workspace_id}}.

    Membership, an administered organization, or superuser — a frozen copy of
    WorkspaceQuerySet.filter_for_user, which a migration must not call.
    """
    User = apps.get_model("user_management", "User")
    Workspace = apps.get_model("workspaces", "Workspace")
    WorkspaceMembership = apps.get_model("workspaces", "WorkspaceMembership")
    OrganizationMembership = apps.get_model("user_management", "OrganizationMembership")

    by_organization = {}
    for organization_id, workspace_id in Workspace.objects.filter(
        archived=False, organization__isnull=False
    ).values_list("organization_id", "id"):
        by_organization.setdefault(organization_id, set()).add(workspace_id)

    reachable = {}
    for user_id, workspace_id in WorkspaceMembership.objects.filter(
        user_id__in=user_ids, workspace__archived=False
    ).values_list("user_id", "workspace_id"):
        reachable.setdefault(user_id, set()).add(workspace_id)

    for user_id, organization_id in OrganizationMembership.objects.filter(
        user_id__in=user_ids, role__in=["owner", "admin"]
    ).values_list("user_id", "organization_id"):
        reachable.setdefault(user_id, set()).update(
            by_organization.get(organization_id, set())
        )

    every_workspace = set(
        Workspace.objects.filter(archived=False).values_list("id", flat=True)
    )
    for user_id in User.objects.filter(id__in=user_ids, is_superuser=True).values_list(
        "id", flat=True
    ):
        reachable[user_id] = every_workspace

    return reachable


def backfill_connections(apps, schema_editor):
    """Give every client that already holds an MCP token the access it has today.

    Grants are explicit lists, so each connection has to be handed the tools and
    workspaces it could already reach, or it would lose access on deploy.
    """
    MCPConnection = apps.get_model("mcp", "MCPConnection")
    pairs = mcp_token_owners(apps)

    MCPConnection.objects.bulk_create(
        [
            MCPConnection(
                user_id=user_id,
                application_id=application_id,
                tools=ALL_TOOLS,
            )
            for user_id, application_id in pairs
        ],
        ignore_conflicts=True,
    )

    reachable = reachable_workspaces(apps, {user_id for user_id, _ in pairs})
    for connection in MCPConnection.objects.all():
        connection.workspaces.set(reachable.get(connection.user_id, set()))


class Migration(migrations.Migration):
    dependencies = [
        ("mcp", "0001_initial"),
        ("user_management", "0044_remove_assistant_feature_flag"),
        ("workspaces", "0064_backfill_bucket_cors"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MCPUser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=(
                "user_management.user",
                hexa.user_management.models.ServicePrincipal,
            ),
            managers=[
                ("objects", hexa.user_management.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="MCPConnection",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tools", models.JSONField(default=list)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mcp_connections",
                        to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mcp_connections",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspaces",
                    models.ManyToManyField(
                        blank=True,
                        related_name="mcp_connections",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "constraints": [
                    models.UniqueConstraint(
                        models.F("user"),
                        models.F("application"),
                        name="mcp_connection_unique_user_application",
                    )
                ],
            },
        ),
        migrations.RunPython(backfill_connections, migrations.RunPython.noop),
    ]
