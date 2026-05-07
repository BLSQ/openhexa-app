import psycopg2
from django.conf import settings
from django.db import migrations
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


def revoke_create_on_public_from_public(apps, schema_editor):
    """
    Strip the inherited `GRANT CREATE ON SCHEMA public TO PUBLIC` from every
    existing workspace DB.

    Cloud SQL's template1.public ACL retained the pre-PG15 default
    (=UC/cloudsqlsuperuser) across pg_upgrade, so each workspace DB cloned from
    template1 inherited CREATE-via-PUBLIC. That let the {db}_ro role create
    tables despite create_read_only_role only granting USAGE + SELECT.

    This is a no-op on DBs already in the modern state (e.g. dev). Per-workspace
    failures (e.g. archived workspace whose DB was dropped) are logged and
    skipped so a single bad workspace can't abort the migration.
    """
    Workspace = apps.get_model("workspaces", "Workspace")

    for workspace in Workspace.objects.all():
        db_name = workspace.db_name
        try:
            conn = get_admin_connection(db_name)
            try:
                with conn.cursor() as cur:
                    cur.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC;")
            finally:
                conn.close()
        except Exception as exc:
            print(f"[0058] Skipping workspace {workspace.id} ({db_name}): {exc}")


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0057_fix_readonly_role_grants"),
    ]

    operations = [
        migrations.RunPython(
            revoke_create_on_public_from_public,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
