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


def grant_create_on_public_to_rw_role(apps, schema_editor):
    """
    Ensure every workspace's RW role has an explicit `GRANT ALL ON SCHEMA public`.

    Workspaces created before the explicit grant was added to
    `create_read_and_write_role` (2025-04) were relying on the pre-PG15
    `GRANT CREATE ON SCHEMA public TO PUBLIC` default. Migration 0058 revoked
    that PUBLIC grant, which stripped CREATE from those RW roles and broke
    pipeline writes (e.g. `df.write_database(..., if_table_exists="replace")`
    fails with "permission denied for schema public").

    Idempotent: re-granting ALL on a schema the role already has full access to
    is a no-op.
    """
    Workspace = apps.get_model("workspaces", "Workspace")

    for workspace in Workspace.objects.all():
        db_name = workspace.db_name
        try:
            conn = get_admin_connection(db_name)
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        sql.SQL("GRANT ALL ON SCHEMA public TO {role}").format(
                            role=sql.Identifier(db_name),
                        )
                    )
            finally:
                conn.close()
        except Exception as exc:
            print(f"[0060] Skipping workspace {workspace.id} ({db_name}): {exc}")


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0059_reassign_objects_owned_by_ro_role"),
    ]

    operations = [
        migrations.RunPython(
            grant_create_on_public_to_rw_role,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
