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


def reassign_objects_owned_by_ro_role(apps, schema_editor):
    """
    Move ownership of any objects owned by `{db_name}_ro` to `{db_name}` (the
    workspace's RW role).

    While the CREATE-via-PUBLIC leak (fixed with migration 0058) was active,
    RO sessions could create tables.

    Those tables ended up owned by the RO role, which made them invisible to the
    OpenHEXA UI, resulting in confusion.

    REASSIGN OWNED BY moves ownership of all such objects (tables,
    sequences, indexes, views, …) from RO to RW within the current database.
    Idempotent: a no-op if RO currently owns nothing.
    """
    Workspace = apps.get_model("workspaces", "Workspace")
    admin_role = settings.WORKSPACES_DATABASE_ROLE

    for workspace in Workspace.objects.all():
        db_name = workspace.db_name
        ro_role = f"{db_name}_ro"
        try:
            conn = get_admin_connection(db_name)
            try:
                with conn.cursor() as cur:
                    # REASSIGN OWNED BY requires the executor to be a member of both the source
                    # and target roles.
                    cur.execute(
                        sql.SQL("GRANT {ro_role} TO {admin_role}").format(
                            ro_role=sql.Identifier(ro_role),
                            admin_role=sql.Identifier(admin_role),
                        )
                    )
                    cur.execute(
                        sql.SQL("REASSIGN OWNED BY {ro_role} TO {rw_role}").format(
                            ro_role=sql.Identifier(ro_role),
                            rw_role=sql.Identifier(db_name),
                        )
                    )
                    cur.execute(
                        sql.SQL("REVOKE {ro_role} FROM {admin_role}").format(
                            ro_role=sql.Identifier(ro_role),
                            admin_role=sql.Identifier(admin_role),
                        )
                    )
            finally:
                conn.close()
        except Exception as exc:
            print(f"[0059] Skipping workspace {workspace.id} ({db_name}): {exc}")


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0058_revoke_create_on_public_from_public"),
    ]

    operations = [
        migrations.RunPython(
            reassign_objects_owned_by_ro_role,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
