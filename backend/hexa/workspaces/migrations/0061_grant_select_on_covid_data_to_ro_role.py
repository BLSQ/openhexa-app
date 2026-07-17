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


def grant_select_on_covid_data(apps, schema_editor):
    """
    Back-fill the read-only role's SELECT grant on the tutorial covid_data table.
    """
    Workspace = apps.get_model("workspaces", "Workspace")

    granted = 0
    skipped = 0
    for workspace in Workspace.objects.filter(db_ro_password__isnull=False):
        db_name = workspace.db_name
        ro_role = f"{db_name}_ro"

        try:
            conn = get_admin_connection(db_name)
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT to_regclass('public.covid_data');")
                    if cur.fetchone()[0] is None:
                        skipped += 1
                        print(
                            f"[0061] Skipping workspace {workspace.id} ({db_name}): "
                            "no covid_data table"
                        )
                        continue
                    cur.execute(
                        sql.SQL("GRANT SELECT ON covid_data TO {role}").format(
                            role=sql.Identifier(ro_role),
                        )
                    )
                    granted += 1
                    print(f"[0061] Granted SELECT on covid_data to {ro_role}")
            finally:
                conn.close()
        except Exception as exc:
            skipped += 1
            print(f"[0061] Skipping workspace {workspace.id} ({db_name}): {exc}")

    print(f"[0061] Done. Granted on {granted} workspace(s), skipped {skipped}.")


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
