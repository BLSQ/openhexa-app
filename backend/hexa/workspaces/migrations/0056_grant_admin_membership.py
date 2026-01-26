import psycopg2
from django.conf import settings
from django.db import migrations
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_admin_connection():
    """Get a connection to the default database using the admin role."""
    host = settings.WORKSPACES_DATABASE_HOST
    port = settings.WORKSPACES_DATABASE_PORT
    admin_role = settings.WORKSPACES_DATABASE_ROLE
    admin_password = settings.WORKSPACES_DATABASE_PASSWORD
    default_db = settings.WORKSPACES_DATABASE_DEFAULT_DB

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=default_db,
        user=admin_role,
        password=admin_password,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def grant_admin_membership(apps, schema_editor):
    """Grant WORKSPACES_DATABASE_ROLE membership in all workspace roles."""
    Workspace = apps.get_model("workspaces", "Workspace")
    admin_role = settings.WORKSPACES_DATABASE_ROLE

    conn = get_admin_connection()
    try:
        with conn.cursor() as cur:
            for workspace in Workspace.objects.all():
                cur.execute(
                    sql.SQL("GRANT {role_name} TO {workspace_database_role}").format(
                        role_name=sql.Identifier(workspace.db_name),
                        workspace_database_role=sql.Identifier(admin_role),
                    )
                )
    finally:
        conn.close()


def reverse_migration(apps, schema_editor):
    """Revoke WORKSPACES_DATABASE_ROLE membership from all workspace roles."""
    Workspace = apps.get_model("workspaces", "Workspace")
    admin_role = settings.WORKSPACES_DATABASE_ROLE

    conn = get_admin_connection()
    try:
        with conn.cursor() as cur:
            for workspace in Workspace.objects.all():
                cur.execute(
                    sql.SQL("REVOKE {role_name} FROM {workspace_database_role}").format(
                        role_name=sql.Identifier(workspace.db_name),
                        workspace_database_role=sql.Identifier(admin_role),
                    )
                )
    finally:
        conn.close()


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0055_alter_workspace_db_ro_password_non_nullable"),
    ]

    operations = [
        migrations.RunPython(
            grant_admin_membership,
            reverse_code=reverse_migration,
        ),
    ]
