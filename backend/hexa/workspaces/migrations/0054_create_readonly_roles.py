import secrets

import psycopg2
from django.conf import settings
from django.db import migrations
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def make_random_password(
    length=16,
    allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789",
):
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def role_exists(cursor, role_name):
    """Check if a PostgreSQL role exists."""
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role_name,))
    return cursor.fetchone() is not None


def create_read_only_role_as_owner(db_name, db_password, ro_password):
    """
    Create a read-only role for a database, connecting as the workspace owner.

    This ensures we have proper permissions to GRANT SELECT on tables
    and ALTER DEFAULT PRIVILEGES, even when the migration role is not a superuser.

    This function is idempotent - it can be run multiple times safely.
    """
    host = settings.WORKSPACES_DATABASE_HOST
    port = settings.WORKSPACES_DATABASE_PORT

    conn = psycopg2.connect(
        host=host, port=port, dbname=db_name, user=db_name, password=db_password
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    ro_role = f"{db_name}_ro"
    try:
        with conn.cursor() as cur:
            # Create role only if it doesn't exist
            if not role_exists(cur, ro_role):
                cur.execute(
                    sql.SQL("CREATE ROLE {role_name} LOGIN PASSWORD {password}").format(
                        role_name=sql.Identifier(ro_role),
                        password=sql.Literal(ro_password),
                    )
                )
            else:
                # Update password if role already exists
                cur.execute(
                    sql.SQL("ALTER ROLE {role_name} WITH PASSWORD {password}").format(
                        role_name=sql.Identifier(ro_role),
                        password=sql.Literal(ro_password),
                    )
                )

            # GRANT statements are idempotent - safe to run multiple times
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
            cur.execute(
                sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role}").format(
                    role=sql.Identifier(ro_role)
                )
            )
            # Set default privileges for future tables created by this role
            cur.execute(
                sql.SQL(
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
                    "GRANT SELECT ON TABLES TO {ro_role}"
                ).format(
                    ro_role=sql.Identifier(ro_role),
                )
            )
    finally:
        conn.close()


def create_readonly_roles_for_existing_workspaces(apps, schema_editor):
    Workspace = apps.get_model("workspaces", "Workspace")

    for workspace in Workspace.objects.filter(db_ro_password__isnull=True):
        ro_password = make_random_password(length=16)
        create_read_only_role_as_owner(
            workspace.db_name, workspace.db_password, ro_password
        )
        workspace.db_ro_password = ro_password
        workspace.save(update_fields=["db_ro_password"])
        print(f"Created read-only role for workspace {workspace.slug}")


def reverse_migration(apps, schema_editor):
    Workspace = apps.get_model("workspaces", "Workspace")
    Workspace.objects.update(db_ro_password=None)


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0053_workspace_db_ro_password"),
    ]

    operations = [
        migrations.RunPython(
            create_readonly_roles_for_existing_workspaces,
            reverse_code=reverse_migration,
        ),
    ]
