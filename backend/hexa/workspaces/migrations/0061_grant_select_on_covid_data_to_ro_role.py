import psycopg2
from django.conf import settings
from django.db import migrations
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_rw_connection(workspace):
    """Connect to a workspace database as its read-write role."""
    conn = psycopg2.connect(
        host=settings.WORKSPACES_DATABASE_HOST,
        port=settings.WORKSPACES_DATABASE_PORT,
        dbname=workspace.db_name,
        user=workspace.db_name,
        password=workspace.db_password,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def grant_select_on_covid_data(apps, schema_editor):
    """
    Back-fill the read-only role's SELECT grant on the tutorial covid_data table.

    Connect as the workspace's read-write role, which owns covid_data (created by
    it on the current path, and reassigned to it via `ALTER TABLE OWNER` on the
    legacy path). An object's owner can always GRANT, so this does not rely on the
    admin role being a superuser or a member of the RW role — both of which are
    false for workspaces created before those grants were introduced.

    Idempotent: re-granting SELECT the RO role already holds is a no-op.
    """
    Workspace = apps.get_model("workspaces", "Workspace")

    total = 0
    granted = 0
    no_table = []
    failed = []
    for workspace in Workspace.objects.all():
        total += 1
        db_name = workspace.db_name
        ro_role = f"{db_name}_ro"

        try:
            conn = get_rw_connection(workspace)
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT to_regclass('public.covid_data');")
                    if cur.fetchone()[0] is None:
                        no_table.append(db_name)
                        continue
                    cur.execute(
                        sql.SQL("GRANT SELECT ON covid_data TO {role}").format(
                            role=sql.Identifier(ro_role),
                        )
                    )
                    granted += 1
            finally:
                conn.close()
        except Exception as exc:
            failed.append(db_name)
            print(f"[0061] Failed on workspace {workspace.id} ({db_name}): {exc}")

    print(
        f"[0061] Done. Granted SELECT on covid_data for {granted}/{total} workspace(s)."
    )
    if no_table:
        print(
            f"[0061] {len(no_table)} without the tutorial table: {', '.join(no_table)}"
        )
    if failed:
        print(f"[0061] {len(failed)} failed: {', '.join(failed)}")


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0060_grant_create_on_public_to_rw_role"),
    ]

    operations = [
        migrations.RunPython(
            grant_select_on_covid_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
