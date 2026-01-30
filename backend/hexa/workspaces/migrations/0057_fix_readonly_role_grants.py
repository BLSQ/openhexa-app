import psycopg2
from django.conf import settings
from django.db import migrations
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_admin_connection(db_name):
    """Get a connection to a specific database using the admin role."""
    host = settings.WORKSPACES_DATABASE_HOST
    port = settings.WORKSPACES_DATABASE_PORT
    admin_role = settings.WORKSPACES_DATABASE_ROLE
    admin_password = settings.WORKSPACES_DATABASE_PASSWORD

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=db_name,
        user=admin_role,
        password=admin_password,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def fix_readonly_role_grants(apps, schema_editor):
    """
    Fix read-only role grants that failed silently in migration 0054.

    The original migration tried to grant privileges using the workspace owner
    connection, but:
    - GRANT CONNECT ON DATABASE requires database ownership (admin has it)
    - GRANT USAGE ON SCHEMA public requires WITH GRANT OPTION (workspace doesn't have it)

    This migration runs those grants as the admin role, which owns the databases.
    """
    Workspace = apps.get_model("workspaces", "Workspace")

    for workspace in Workspace.objects.filter(db_ro_password__isnull=False):
        db_name = workspace.db_name
        ro_role = f"{db_name}_ro"

        conn = get_admin_connection(db_name)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("GRANT CONNECT ON DATABASE {db_name} TO {role}").format(
                        db_name=sql.Identifier(db_name),
                        role=sql.Identifier(ro_role),
                    )
                )
                cur.execute(
                    sql.SQL("GRANT USAGE ON SCHEMA public TO {role}").format(
                        role=sql.Identifier(ro_role)
                    )
                )
        finally:
            conn.close()


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0056_grant_admin_membership"),
    ]

    operations = [
        migrations.RunPython(
            fix_readonly_role_grants,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
